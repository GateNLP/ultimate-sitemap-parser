"""Objects that are to be returned by the sitemap parser."""

import abc
import datetime
from decimal import Decimal
from enum import Enum, unique
from typing import List, Optional, Set

import attr

SITEMAP_PAGE_DEFAULT_PRIORITY = Decimal('0.5')
"""Default sitemap page priority, as per the spec."""


@attr.s(slots=True, frozen=True)
class SitemapNewsStory(object):
    """Single story derived from Google News XML sitemap."""

    # Spec defines that some of the properties below are "required" but in practice not every website provides the
    # required properties. So, we require only "title" and "publish_date" to be set.

    title = attr.ib(type=str)
    """Story title."""

    publish_date = attr.ib(type=datetime.datetime)
    """Story publication date."""

    publication_name = attr.ib(type=Optional[str], default=None)
    """Name of the news publication in which the article appears in."""

    publication_language = attr.ib(type=Optional[str], default=None)
    """Primary language of the news publication in which the article appears in.

    It should be an ISO 639 Language Code (either 2 or 3 letters)."""

    access = attr.ib(type=Optional[str], default=None)
    """Accessibility of the article."""

    genres = attr.ib(type=List[str], factory=list)
    """List of properties characterizing the content of the article, such as "PressRelease" or "UserGenerated"."""

    keywords = attr.ib(type=List[str], factory=list)
    """List of keywords describing the topic of the article."""

    stock_tickers = attr.ib(type=List[str], factory=list)
    """Comma-separated list of up to 5 stock tickers that are the main subject of the article.

    Each ticker must be prefixed by the name of its stock exchange, and must match its entry in Google Finance.
    For example, "NASDAQ:AMAT" (but not "NASD:AMAT"), or "BOM:500325" (but not "BOM:RIL")."""


@unique
class SitemapPageChangeFrequency(Enum):
    """Change frequency of a sitemap URL."""
    ALWAYS = 'always'
    HOURLY = 'hourly'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'
    NEVER = 'never'

    @classmethod
    def has_value(cls, value: str) -> bool:
        """Test if enum has specified value."""
        return any(value == item.value for item in cls)


@attr.s(slots=True, frozen=True)
class SitemapPage(object):
    """Single sitemap-derived page."""

    url = attr.ib(type=str, hash=True)
    """Page URL."""

    priority = attr.ib(type=Decimal, default=SITEMAP_PAGE_DEFAULT_PRIORITY, hash=False)
    """Priority of this URL relative to other URLs on your site."""

    last_modified = attr.ib(type=Optional[datetime.datetime], default=None, hash=False)
    """Date of last modification of the URL."""

    change_frequency = attr.ib(type=Optional[SitemapPageChangeFrequency], default=None, hash=False)
    """Change frequency of a sitemap URL."""

    news_story = attr.ib(type=Optional[SitemapNewsStory], default=None, hash=False)
    """Google News story attached to the URL."""


@attr.s(slots=True, frozen=True)
class AbstractSitemap(object, metaclass=abc.ABCMeta):
    """Abstract sitemap."""

    url = attr.ib(type=str, hash=True)
    """Sitemap URL."""

    @abc.abstractmethod
    def all_pages(self) -> Set[SitemapPage]:
        """Recursively return all stories from this sitemap and linked sitemaps."""
        raise NotImplementedError("Abstract method")


@attr.s(slots=True, frozen=True)
class InvalidSitemap(AbstractSitemap):
    """Invalid sitemap, e.g. the one that can't be parsed."""

    reason = attr.ib(type=str, hash=False)
    """Reason why the sitemap is deemed invalid."""

    def all_pages(self) -> Set[SitemapPage]:
        return set()


@attr.s(slots=True, frozen=True)
class AbstractPagesSitemap(AbstractSitemap, metaclass=abc.ABCMeta):
    """Abstract sitemap that contains URLs to pages."""

    pages = attr.ib(type=List[SitemapPage], hash=False)
    """URLs to pages that were found in a sitemap."""

    def all_pages(self) -> Set[SitemapPage]:
        return set(self.pages)


@attr.s(slots=True, frozen=True)
class PagesXMLSitemap(AbstractPagesSitemap):
    """XML sitemap that contains URLs to pages."""
    pass


@attr.s(slots=True, frozen=True)
class PagesTextSitemap(AbstractPagesSitemap):
    """Plain text sitemap that contains URLs to pages."""
    pass


@attr.s(slots=True, frozen=True)
class PagesRSSSitemap(AbstractPagesSitemap):
    """RSS 2.0 sitemap that contains URLs to pages."""
    pass


@attr.s(slots=True, frozen=True)
class PagesAtomSitemap(AbstractPagesSitemap):
    """RSS 0.3 / 1.0 sitemap that contains URLs to pages."""
    pass


@attr.s(slots=True, frozen=True)
class AbstractIndexSitemap(AbstractSitemap):
    """Abstract sitemap with URLs to other sitemaps."""

    sub_sitemaps = attr.ib(type=List[AbstractSitemap], hash=False)
    """Sub-sitemaps that are linked to from this sitemap."""

    def all_pages(self) -> Set[SitemapPage]:
        pages = set()
        for sub_sitemap in self.sub_sitemaps:
            pages |= sub_sitemap.all_pages()
        return pages


@attr.s(slots=True, frozen=True)
class IndexWebsiteSitemap(AbstractIndexSitemap):
    """Website's root sitemaps, including robots.txt and extra ones."""
    pass


@attr.s(slots=True, frozen=True)
class IndexXMLSitemap(AbstractIndexSitemap):
    """XML sitemap with URLs to other sitemaps."""
    pass


@attr.s(slots=True, frozen=True)
class IndexRobotsTxtSitemap(AbstractIndexSitemap):
    """robots.txt sitemap with URLs to other sitemaps."""
    pass
