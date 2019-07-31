"""Sitemap fetchers and parsers."""

import abc
import re
import xml.parsers.expat
from collections import OrderedDict
from decimal import Decimal
from typing import Optional, Dict

from .exceptions import SitemapException, SitemapXMLParsingException
from .helpers import (
    html_unescape_strip,
    parse_iso8601_date,
    get_url_retry_on_client_errors,
    ungzipped_response_content,
    is_http_url,
    parse_rfc2822_date,
)
from .log import create_logger
from .objects.page import (
    SitemapPage,
    SitemapNewsStory,
    SitemapPageChangeFrequency,
    SITEMAP_PAGE_DEFAULT_PRIORITY,
)
from .objects.sitemap import (
    AbstractSitemap,
    InvalidSitemap,
    IndexRobotsTxtSitemap,
    IndexXMLSitemap,
    PagesXMLSitemap,
    PagesTextSitemap,
    PagesRSSSitemap,
    PagesAtomSitemap,
)
from .web_client.abstract_client import (
    AbstractWebClient,
    AbstractWebClientSuccessResponse,
    WebClientErrorResponse,
)
from .web_client.requests_client import RequestsWebClient

log = create_logger(__name__)


class SitemapFetcher(object):
    """robots.txt / XML / plain text sitemap fetcher."""

    __MAX_SITEMAP_SIZE = 100 * 1024 * 1024
    """Max. uncompressed sitemap size.

    Spec says it might be up to 50 MB but let's go for the full 100 MB here."""

    __MAX_RECURSION_LEVEL = 10
    """Max. recursion level in iterating over sub-sitemaps."""

    __slots__ = [
        '_url',
        '_recursion_level',
        '_web_client',
    ]

    def __init__(self, url: str, recursion_level: int, web_client: Optional[AbstractWebClient] = None):

        if recursion_level > self.__MAX_RECURSION_LEVEL:
            raise SitemapException("Recursion level exceeded {} for URL {}.".format(self.__MAX_RECURSION_LEVEL, url))

        if not is_http_url(url):
            raise SitemapException("URL {} is not a HTTP(s) URL.".format(url))

        if not web_client:
            web_client = RequestsWebClient()

        web_client.set_max_response_data_length(self.__MAX_SITEMAP_SIZE)

        self._url = url
        self._web_client = web_client
        self._recursion_level = recursion_level

    def sitemap(self) -> AbstractSitemap:
        log.info("Fetching level {} sitemap from {}...".format(self._recursion_level, self._url))
        response = get_url_retry_on_client_errors(url=self._url, web_client=self._web_client)

        if isinstance(response, WebClientErrorResponse):
            return InvalidSitemap(
                url=self._url,
                reason="Unable to fetch sitemap from {}: {}".format(self._url, response.message()),
            )

        assert isinstance(response, AbstractWebClientSuccessResponse)

        response_content = ungzipped_response_content(url=self._url, response=response)

        # MIME types returned in Content-Type are unpredictable, so peek into the content instead
        if response_content[:20].strip().startswith('<'):
            # XML sitemap (the specific kind is to be determined later)
            parser = XMLSitemapParser(
                url=self._url,
                content=response_content,
                recursion_level=self._recursion_level,
                web_client=self._web_client,
            )

        else:
            # Assume that it's some sort of a text file (robots.txt or plain text sitemap)
            if self._url.endswith('/robots.txt'):
                parser = IndexRobotsTxtSitemapParser(
                    url=self._url,
                    content=response_content,
                    recursion_level=self._recursion_level,
                    web_client=self._web_client,
                )
            else:
                parser = PlainTextSitemapParser(
                    url=self._url,
                    content=response_content,
                    recursion_level=self._recursion_level,
                    web_client=self._web_client,
                )

        log.info("Parsing sitemap from URL {}...".format(self._url))
        sitemap = parser.sitemap()

        return sitemap


class AbstractSitemapParser(object, metaclass=abc.ABCMeta):
    """Abstract robots.txt / XML / plain text sitemap parser."""

    __slots__ = [
        '_url',
        '_content',
        '_web_client',
        '_recursion_level',
    ]

    def __init__(self, url: str, content: str, recursion_level: int, web_client: AbstractWebClient):
        self._url = url
        self._content = content
        self._recursion_level = recursion_level
        self._web_client = web_client

    @abc.abstractmethod
    def sitemap(self) -> AbstractSitemap:
        raise NotImplementedError("Abstract method.")


class IndexRobotsTxtSitemapParser(AbstractSitemapParser):
    """robots.txt index sitemap parser."""

    def __init__(self, url: str, content: str, recursion_level: int, web_client: AbstractWebClient):
        super().__init__(url=url, content=content, recursion_level=recursion_level, web_client=web_client)

        if not self._url.endswith('/robots.txt'):
            raise SitemapException("URL does not look like robots.txt URL: {}".format(self._url))

    def sitemap(self) -> AbstractSitemap:

        # Serves as an ordered set because we want to deduplicate URLs but also retain the order
        sitemap_urls = OrderedDict()

        for robots_txt_line in self._content.splitlines():
            robots_txt_line = robots_txt_line.strip()
            # robots.txt is supposed to be case sensitive but who cares in these Node.js times?
            robots_txt_line = robots_txt_line.lower()
            sitemap_match = re.search(r'^site-?map:\s*(.+?)$', robots_txt_line, flags=re.IGNORECASE)
            if sitemap_match:
                sitemap_url = sitemap_match.group(1)
                if is_http_url(sitemap_url):
                    sitemap_urls[sitemap_url] = True
                else:
                    log.warning("Sitemap URL {} doesn't look like an URL, skipping".format(sitemap_url))

        sub_sitemaps = []

        for sitemap_url in sitemap_urls.keys():
            fetcher = SitemapFetcher(
                url=sitemap_url,
                recursion_level=self._recursion_level,
                web_client=self._web_client,
            )
            fetched_sitemap = fetcher.sitemap()
            sub_sitemaps.append(fetched_sitemap)

        index_sitemap = IndexRobotsTxtSitemap(url=self._url, sub_sitemaps=sub_sitemaps)

        return index_sitemap


class PlainTextSitemapParser(AbstractSitemapParser):
    """Plain text sitemap parser."""

    def sitemap(self) -> AbstractSitemap:

        story_urls = OrderedDict()

        for story_url in self._content.splitlines():
            story_url = story_url.strip()
            if not story_url:
                continue
            if is_http_url(story_url):
                story_urls[story_url] = True
            else:
                log.warning("Story URL {} doesn't look like an URL, skipping".format(story_url))

        pages = []
        for page_url in story_urls.keys():
            page = SitemapPage(url=page_url)
            pages.append(page)

        text_sitemap = PagesTextSitemap(url=self._url, pages=pages)

        return text_sitemap


class XMLSitemapParser(AbstractSitemapParser):
    """XML sitemap parser."""

    __XML_NAMESPACE_SEPARATOR = ' '

    __slots__ = [
        '_concrete_parser',
    ]

    def __init__(self, url: str, content: str, recursion_level: int, web_client: AbstractWebClient):
        super().__init__(url=url, content=content, recursion_level=recursion_level, web_client=web_client)

        # Will be initialized when the type of sitemap is known
        self._concrete_parser = None

    def sitemap(self) -> AbstractSitemap:

        parser = xml.parsers.expat.ParserCreate(namespace_separator=self.__XML_NAMESPACE_SEPARATOR)
        parser.StartElementHandler = self._xml_element_start
        parser.EndElementHandler = self._xml_element_end
        parser.CharacterDataHandler = self._xml_char_data

        try:
            is_final = True
            parser.Parse(self._content, is_final)
        except Exception as ex:
            # Some sitemap XML files might end abruptly because webservers might be timing out on returning huge XML
            # files so don't return InvalidSitemap() but try to get as much pages as possible
            log.error("Parsing sitemap from URL {} failed: {}".format(self._url, ex))

        if not self._concrete_parser:
            return InvalidSitemap(
                url=self._url,
                reason="No parsers support sitemap from {}".format(self._url),
            )

        return self._concrete_parser.sitemap()

    @classmethod
    def __normalize_xml_element_name(cls, name: str):
        """
        Replace the namespace URL in the argument element name with internal namespace.

        * Elements from http://www.sitemaps.org/schemas/sitemap/0.9 namespace will be prefixed with "sitemap:",
          e.g. "<loc>" will become "<sitemap:loc>"

        * Elements from http://www.google.com/schemas/sitemap-news/0.9 namespace will be prefixed with "news:",
          e.g. "<publication>" will become "<news:publication>"

        For non-sitemap namespaces, return the element name with the namespace stripped.

        :param name: Namespace URL plus XML element name, e.g. "http://www.sitemaps.org/schemas/sitemap/0.9 loc"
        :return: Internal namespace name plus element name, e.g. "sitemap loc"
        """

        name_parts = name.split(cls.__XML_NAMESPACE_SEPARATOR)

        if len(name_parts) == 1:
            namespace_url = ''
            name = name_parts[0]

        elif len(name_parts) == 2:
            namespace_url = name_parts[0]
            name = name_parts[1]

        else:
            raise SitemapXMLParsingException("Unable to determine namespace for element '{}'".format(name))

        if '/sitemap/' in namespace_url:
            name = 'sitemap:{}'.format(name)
        elif '/sitemap-news/' in namespace_url:
            name = 'news:{}'.format(name)
        else:
            # We don't care about the rest of the namespaces, so just keep the plain element name
            pass

        return name

    def _xml_element_start(self, name: str, attrs: Dict[str, str]) -> None:

        name = self.__normalize_xml_element_name(name)

        if self._concrete_parser:
            self._concrete_parser.xml_element_start(name=name, attrs=attrs)

        else:

            # Root element -- initialize concrete parser
            if name == 'sitemap:urlset':
                self._concrete_parser = PagesXMLSitemapParser(
                    url=self._url,
                )

            elif name == 'sitemap:sitemapindex':
                self._concrete_parser = IndexXMLSitemapParser(
                    url=self._url,
                    web_client=self._web_client,
                    recursion_level=self._recursion_level,
                )

            elif name == 'rss':
                self._concrete_parser = PagesRSSSitemapParser(
                    url=self._url,
                )

            elif name == 'feed':
                self._concrete_parser = PagesAtomSitemapParser(
                    url=self._url,
                )

            else:
                raise SitemapXMLParsingException("Unsupported root element '{}'.".format(name))

    def _xml_element_end(self, name: str) -> None:

        name = self.__normalize_xml_element_name(name)

        if not self._concrete_parser:
            raise SitemapXMLParsingException("Concrete sitemap parser should be set by now.")

        self._concrete_parser.xml_element_end(name=name)

    def _xml_char_data(self, data: str) -> None:

        if not self._concrete_parser:
            raise SitemapXMLParsingException("Concrete sitemap parser should be set by now.")

        self._concrete_parser.xml_char_data(data=data)


class AbstractXMLSitemapParser(object, metaclass=abc.ABCMeta):
    """
    Abstract XML sitemap parser.
    """

    __slots__ = [
        # URL of the sitemap that is being parsed
        '_url',

        # Last encountered character data
        '_last_char_data',

        '_last_handler_call_was_xml_char_data',
    ]

    def __init__(self, url: str):
        self._url = url
        self._last_char_data = ''
        self._last_handler_call_was_xml_char_data = False

    def xml_element_start(self, name: str, attrs: Dict[str, str]) -> None:
        self._last_handler_call_was_xml_char_data = False
        pass

    def xml_element_end(self, name: str) -> None:
        # End of any element always resets last encountered character data
        self._last_char_data = ''
        self._last_handler_call_was_xml_char_data = False

    def xml_char_data(self, data: str) -> None:
        # Handler might be called multiple times for what essentially is a single string, e.g. in case of entities
        # ("ABC &amp; DEF"), so this is why we're appending
        if self._last_handler_call_was_xml_char_data:
            self._last_char_data += data
        else:
            self._last_char_data = data

        self._last_handler_call_was_xml_char_data = True

    @abc.abstractmethod
    def sitemap(self) -> AbstractSitemap:
        raise NotImplementedError("Abstract method.")


class IndexXMLSitemapParser(AbstractXMLSitemapParser):
    """
    Index XML sitemap parser.
    """

    __slots__ = [
        '_web_client',
        '_recursion_level',

        # List of sub-sitemap URLs found in this index sitemap
        '_sub_sitemap_urls',
    ]

    def __init__(self, url: str, web_client: AbstractWebClient, recursion_level: int):
        super().__init__(url=url)

        self._web_client = web_client
        self._recursion_level = recursion_level
        self._sub_sitemap_urls = []

    def xml_element_end(self, name: str) -> None:

        if name == 'sitemap:loc':
            sub_sitemap_url = html_unescape_strip(self._last_char_data)
            if not is_http_url(sub_sitemap_url):
                log.warning("Sub-sitemap URL does not look like one: {}".format(sub_sitemap_url))

            else:
                if sub_sitemap_url not in self._sub_sitemap_urls:
                    self._sub_sitemap_urls.append(sub_sitemap_url)

        super().xml_element_end(name=name)

    def sitemap(self) -> AbstractSitemap:

        sub_sitemaps = []

        for sub_sitemap_url in self._sub_sitemap_urls:

            # URL might be invalid, or recursion limit might have been reached
            try:
                fetcher = SitemapFetcher(url=sub_sitemap_url,
                                         recursion_level=self._recursion_level + 1,
                                         web_client=self._web_client)
                fetched_sitemap = fetcher.sitemap()
            except Exception as ex:
                fetched_sitemap = InvalidSitemap(
                    url=sub_sitemap_url,
                    reason="Unable to add sub-sitemap from URL {}: {}".format(sub_sitemap_url, str(ex)),
                )

            sub_sitemaps.append(fetched_sitemap)

        index_sitemap = IndexXMLSitemap(url=self._url, sub_sitemaps=sub_sitemaps)

        return index_sitemap


class PagesXMLSitemapParser(AbstractXMLSitemapParser):
    """
    Pages XML sitemap parser.
    """

    class Page(object):
        """Simple data class for holding various properties for a single <url> entry while parsing."""

        __slots__ = [
            'url',
            'last_modified',
            'change_frequency',
            'priority',
            'news_title',
            'news_publish_date',
            'news_publication_name',
            'news_publication_language',
            'news_access',
            'news_genres',
            'news_keywords',
            'news_stock_tickers',
        ]

        def __init__(self):
            self.url = None
            self.last_modified = None
            self.change_frequency = None
            self.priority = None
            self.news_title = None
            self.news_publish_date = None
            self.news_publication_name = None
            self.news_publication_language = None
            self.news_access = None
            self.news_genres = None
            self.news_keywords = None
            self.news_stock_tickers = None

        def __hash__(self):
            return hash((
                # Hash only the URL to be able to find unique ones
                self.url,
            ))

        def page(self) -> Optional[SitemapPage]:
            """Return constructed sitemap page if one has been completed, otherwise None."""

            # Required
            url = html_unescape_strip(self.url)
            if not url:
                log.error("URL is unset")
                return None

            last_modified = html_unescape_strip(self.last_modified)
            if last_modified:
                last_modified = parse_iso8601_date(last_modified)

            change_frequency = html_unescape_strip(self.change_frequency)
            if change_frequency:
                change_frequency = change_frequency.lower()
                if SitemapPageChangeFrequency.has_value(change_frequency):
                    change_frequency = SitemapPageChangeFrequency(change_frequency)
                else:
                    log.warning("Invalid change frequency, defaulting to 'always'.".format(change_frequency))
                    change_frequency = SitemapPageChangeFrequency.ALWAYS
                assert isinstance(change_frequency, SitemapPageChangeFrequency)

            priority = html_unescape_strip(self.priority)
            if priority:
                priority = Decimal(priority)

                comp_zero = priority.compare(Decimal('0.0'))
                comp_one = priority.compare(Decimal('1.0'))
                if comp_zero in (Decimal('0'), Decimal('1') and comp_one in (Decimal('0'), Decimal('-1'))):
                    # 0 <= priority <= 1
                    pass
                else:
                    log.warning("Priority is not within 0 and 1: {}".format(priority))
                    priority = SITEMAP_PAGE_DEFAULT_PRIORITY

            else:
                priority = SITEMAP_PAGE_DEFAULT_PRIORITY

            news_title = html_unescape_strip(self.news_title)

            news_publish_date = html_unescape_strip(self.news_publish_date)
            if news_publish_date:
                news_publish_date = parse_iso8601_date(date_string=news_publish_date)

            news_publication_name = html_unescape_strip(self.news_publication_name)
            news_publication_language = html_unescape_strip(self.news_publication_language)
            news_access = html_unescape_strip(self.news_access)

            news_genres = html_unescape_strip(self.news_genres)
            if news_genres:
                news_genres = [x.strip() for x in news_genres.split(',')]
            else:
                news_genres = []

            news_keywords = html_unescape_strip(self.news_keywords)
            if news_keywords:
                news_keywords = [x.strip() for x in news_keywords.split(',')]
            else:
                news_keywords = []

            news_stock_tickers = html_unescape_strip(self.news_stock_tickers)
            if news_stock_tickers:
                news_stock_tickers = [x.strip() for x in news_stock_tickers.split(',')]
            else:
                news_stock_tickers = []

            sitemap_news_story = None
            if news_title and news_publish_date:
                sitemap_news_story = SitemapNewsStory(
                    title=news_title,
                    publish_date=news_publish_date,
                    publication_name=news_publication_name,
                    publication_language=news_publication_language,
                    access=news_access,
                    genres=news_genres,
                    keywords=news_keywords,
                    stock_tickers=news_stock_tickers,
                )

            return SitemapPage(
                url=url,
                last_modified=last_modified,
                change_frequency=change_frequency,
                priority=priority,
                news_story=sitemap_news_story,
            )

    __slots__ = [
        '_current_page',
        '_pages',
    ]

    def __init__(self, url: str):
        super().__init__(url=url)

        self._current_page = None
        self._pages = []

    def xml_element_start(self, name: str, attrs: Dict[str, str]) -> None:

        super().xml_element_start(name=name, attrs=attrs)

        if name == 'sitemap:url':
            if self._current_page:
                raise SitemapXMLParsingException("Page is expected to be unset by <url>.")
            self._current_page = self.Page()

    def __require_last_char_data_to_be_set(self, name: str) -> None:
        if not self._last_char_data:
            raise SitemapXMLParsingException(
                "Character data is expected to be set at the end of <{}>.".format(name)
            )

    def xml_element_end(self, name: str) -> None:

        if not self._current_page and name != 'sitemap:urlset':
            raise SitemapXMLParsingException("Page is expected to be set at the end of <{}>.".format(name))

        if name == 'sitemap:url':
            if self._current_page not in self._pages:
                self._pages.append(self._current_page)
            self._current_page = None

        else:

            if name == 'sitemap:loc':
                # Every entry must have <loc>
                self.__require_last_char_data_to_be_set(name=name)
                self._current_page.url = self._last_char_data

            elif name == 'sitemap:lastmod':
                # Element might be present but character data might be empty
                self._current_page.last_modified = self._last_char_data

            elif name == 'sitemap:changefreq':
                # Element might be present but character data might be empty
                self._current_page.change_frequency = self._last_char_data

            elif name == 'sitemap:priority':
                # Element might be present but character data might be empty
                self._current_page.priority = self._last_char_data

            elif name == 'news:name':  # news/publication/name
                # Element might be present but character data might be empty
                self._current_page.news_publication_name = self._last_char_data

            elif name == 'news:language':  # news/publication/language
                # Element might be present but character data might be empty
                self._current_page.news_publication_language = self._last_char_data

            elif name == 'news:publication_date':
                # Element might be present but character data might be empty
                self._current_page.news_publish_date = self._last_char_data

            elif name == 'news:title':
                # Every Google News sitemap entry must have <title>
                self.__require_last_char_data_to_be_set(name=name)
                self._current_page.news_title = self._last_char_data

            elif name == 'news:access':
                # Element might be present but character data might be empty
                self._current_page.news_access = self._last_char_data

            elif name == 'news:keywords':
                # Element might be present but character data might be empty
                self._current_page.news_keywords = self._last_char_data

            elif name == 'news:stock_tickers':
                # Element might be present but character data might be empty
                self._current_page.news_stock_tickers = self._last_char_data

        super().xml_element_end(name=name)

    def sitemap(self) -> AbstractSitemap:

        pages = []

        for page_row in self._pages:
            page = page_row.page()
            if page:
                pages.append(page)

        pages_sitemap = PagesXMLSitemap(url=self._url, pages=pages)

        return pages_sitemap


class PagesRSSSitemapParser(AbstractXMLSitemapParser):
    """
    Pages RSS 2.0 sitemap parser.

    https://validator.w3.org/feed/docs/rss2.html
    """

    class Page(object):
        """
        Simple data class for holding various properties for a single <item> entry while parsing.
        """

        __slots__ = [
            'link',
            'title',
            'description',
            'publication_date',
        ]

        def __init__(self):
            self.link = None
            self.title = None
            self.description = None
            self.publication_date = None

        def __hash__(self):
            return hash((
                # Hash only the URL
                self.link,
            ))

        def page(self) -> Optional[SitemapPage]:
            """Return constructed sitemap page if one has been completed, otherwise None."""

            # Required
            link = html_unescape_strip(self.link)
            if not link:
                log.error("Link is unset")
                return None

            title = html_unescape_strip(self.title)
            description = html_unescape_strip(self.description)
            if not (title or description):
                log.error("Both title and description are unset")
                return None

            publication_date = html_unescape_strip(self.publication_date)
            if publication_date:
                publication_date = parse_rfc2822_date(publication_date)

            return SitemapPage(
                url=link,
                news_story=SitemapNewsStory(
                    title=title or description,
                    publish_date=publication_date,
                ),
            )

    __slots__ = [
        '_current_page',
        '_pages',
    ]

    def __init__(self, url: str):
        super().__init__(url=url)

        self._current_page = None
        self._pages = []

    def xml_element_start(self, name: str, attrs: Dict[str, str]) -> None:

        super().xml_element_start(name=name, attrs=attrs)

        if name == 'item':
            if self._current_page:
                raise SitemapXMLParsingException("Page is expected to be unset by <item>.")
            self._current_page = self.Page()

    def __require_last_char_data_to_be_set(self, name: str) -> None:
        if not self._last_char_data:
            raise SitemapXMLParsingException(
                "Character data is expected to be set at the end of <{}>.".format(name)
            )

    def xml_element_end(self, name: str) -> None:

        # If within <item> already
        if self._current_page:

            if name == 'item':
                if self._current_page not in self._pages:
                    self._pages.append(self._current_page)
                self._current_page = None

            else:

                if name == 'link':
                    # Every entry must have <link>
                    self.__require_last_char_data_to_be_set(name=name)
                    self._current_page.link = self._last_char_data

                elif name == 'title':
                    # Title (if set) can't be empty
                    self.__require_last_char_data_to_be_set(name=name)
                    self._current_page.title = self._last_char_data

                elif name == 'description':
                    # Description (if set) can't be empty
                    self.__require_last_char_data_to_be_set(name=name)
                    self._current_page.description = self._last_char_data

                elif name == 'pubDate':
                    # Element might be present but character data might be empty
                    self._current_page.publication_date = self._last_char_data

        super().xml_element_end(name=name)

    def sitemap(self) -> AbstractSitemap:

        pages = []

        for page_row in self._pages:
            page = page_row.page()
            if page:
                pages.append(page)

        pages_sitemap = PagesRSSSitemap(url=self._url, pages=pages)

        return pages_sitemap


class PagesAtomSitemapParser(AbstractXMLSitemapParser):
    """
    Pages Atom 0.3 / 1.0 sitemap parser.

    https://github.com/simplepie/simplepie-ng/wiki/Spec:-Atom-0.3
    https://www.ietf.org/rfc/rfc4287.txt
    http://rakaz.nl/2005/07/moving-from-atom-03-to-10.html
    """

    # FIXME merge with RSS parser class as there are too many similarities

    class Page(object):
        """Simple data class for holding various properties for a single <entry> entry while parsing."""

        __slots__ = [
            'link',
            'title',
            'description',
            'publication_date',
        ]

        def __init__(self):
            self.link = None
            self.title = None
            self.description = None
            self.publication_date = None

        def __hash__(self):
            return hash((
                # Hash only the URL
                self.link,
            ))

        def page(self) -> Optional[SitemapPage]:
            """Return constructed sitemap page if one has been completed, otherwise None."""

            # Required
            link = html_unescape_strip(self.link)
            if not link:
                log.error("Link is unset")
                return None

            title = html_unescape_strip(self.title)
            description = html_unescape_strip(self.description)
            if not (title or description):
                log.error("Both title and description are unset")
                return None

            publication_date = html_unescape_strip(self.publication_date)
            if publication_date:
                publication_date = parse_rfc2822_date(publication_date)

            return SitemapPage(
                url=link,
                news_story=SitemapNewsStory(
                    title=title or description,
                    publish_date=publication_date,
                ),
            )

    __slots__ = [
        '_current_page',
        '_pages',
        '_last_link_rel_self_href',
    ]

    def __init__(self, url: str):
        super().__init__(url=url)

        self._current_page = None
        self._pages = []
        self._last_link_rel_self_href = None

    def xml_element_start(self, name: str, attrs: Dict[str, str]) -> None:

        super().xml_element_start(name=name, attrs=attrs)

        if name == 'entry':
            if self._current_page:
                raise SitemapXMLParsingException("Page is expected to be unset by <entry>.")
            self._current_page = self.Page()

        elif name == 'link':
            if self._current_page:
                if attrs.get('rel', 'self').lower() == 'self' or self._last_link_rel_self_href is None:
                    self._last_link_rel_self_href = attrs.get('href', None)

    def __require_last_char_data_to_be_set(self, name: str) -> None:
        if not self._last_char_data:
            raise SitemapXMLParsingException(
                "Character data is expected to be set at the end of <{}>.".format(name)
            )

    def xml_element_end(self, name: str) -> None:

        # If within <entry> already
        if self._current_page:

            if name == 'entry':

                if self._last_link_rel_self_href:
                    self._current_page.link = self._last_link_rel_self_href
                    self._last_link_rel_self_href = None

                    if self._current_page not in self._pages:
                        self._pages.append(self._current_page)

                self._current_page = None

            else:

                if name == 'title':
                    # Title (if set) can't be empty
                    self.__require_last_char_data_to_be_set(name=name)
                    self._current_page.title = self._last_char_data

                elif name == 'tagline' or name == 'summary':
                    # Description (if set) can't be empty
                    self.__require_last_char_data_to_be_set(name=name)
                    self._current_page.description = self._last_char_data

                elif name == 'issued' or name == 'published':
                    # Element might be present but character data might be empty
                    self._current_page.publication_date = self._last_char_data

                elif name == 'updated':
                    # No 'issued' or 'published' were set before
                    if not self._current_page.publication_date:
                        self._current_page.publication_date = self._last_char_data

        super().xml_element_end(name=name)

    def sitemap(self) -> AbstractSitemap:

        pages = []

        for page_row in self._pages:
            page = page_row.page()
            if page:
                pages.append(page)

        pages_sitemap = PagesAtomSitemap(url=self._url, pages=pages)

        return pages_sitemap
