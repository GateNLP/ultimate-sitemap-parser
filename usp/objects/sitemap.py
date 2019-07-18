"""Objects that represent one of the found sitemaps."""

import abc
import os
import pickle
import tempfile
from typing import List, Iterator

from .page import SitemapPage


class AbstractSitemap(object, metaclass=abc.ABCMeta):
    """
    Abstract sitemap.
    """

    __slots__ = [
        '__url',
    ]

    def __init__(self, url: str):
        """
        Initialize a new sitemap.

        :param url: Sitemap URL.
        """
        self.__url = url

    def __eq__(self, other) -> bool:
        if not isinstance(other, AbstractSitemap):
            raise NotImplemented

        if self.url != other.url:
            return False

        return True

    def __hash__(self):
        return hash((
            self.url,
        ))

    def __repr__(self):
        return (
            "{self.__class__.__name__}("
            "url={self.url}"
            ")"
        ).format(self=self)

    @property
    def url(self) -> str:
        """
        Return sitemap URL.

        :return: Sitemap URL.
        """
        return self.__url

    @abc.abstractmethod
    def all_pages(self) -> Iterator[SitemapPage]:
        """
        Return iterator which yields all pages of this sitemap and linked sitemaps (if any).

        :return: Iterator which yields all pages of this sitemap and linked sitemaps (if any).
        """
        raise NotImplementedError("Abstract method")


class InvalidSitemap(AbstractSitemap):
    """Invalid sitemap, e.g. the one that can't be parsed."""

    __slots__ = [
        '__reason',
    ]

    def __init__(self, url: str, reason: str):
        """
        Initialize a new invalid sitemap.

        :param url: Sitemap URL.
        :param reason: Reason why the sitemap is deemed invalid.
        """
        super().__init__(url=url)
        self.__reason = reason

    def __eq__(self, other) -> bool:
        if not isinstance(other, InvalidSitemap):
            raise NotImplemented

        if self.url != other.url:
            return False

        if self.reason != other.reason:
            return False

        return True

    def __repr__(self):
        return (
            "{self.__class__.__name__}("
            "url={self.url}, "
            "reason={self.reason}"
            ")"
        ).format(self=self)

    @property
    def reason(self) -> str:
        """
        Return reason why the sitemap is deemed invalid.

        :return: Reason why the sitemap is deemed invalid.
        """
        return self.__reason

    def all_pages(self) -> Iterator[SitemapPage]:
        """
        Return iterator which yields all pages of this sitemap and linked sitemaps (if any).

        :return: Iterator which yields all pages of this sitemap and linked sitemaps (if any).
        """
        yield from []


class AbstractPagesSitemap(AbstractSitemap, metaclass=abc.ABCMeta):
    """Abstract sitemap that contains URLs to pages."""

    __slots__ = [
        '__pages_temp_file_path',
    ]

    def __init__(self, url: str, pages: List[SitemapPage]):
        """
        Initialize new pages sitemap.

        :param url: Sitemap URL.
        :param pages: List of pages found in a sitemap.
        """
        super().__init__(url=url)

        temp_file, self.__pages_temp_file_path = tempfile.mkstemp()
        with os.fdopen(temp_file, 'wb') as tmp:
            pickle.dump(pages, tmp, protocol=pickle.HIGHEST_PROTOCOL)

    def __del__(self):
        os.unlink(self.__pages_temp_file_path)

    def __eq__(self, other) -> bool:
        if not isinstance(other, AbstractPagesSitemap):
            raise NotImplemented

        if self.url != other.url:
            return False

        if self.pages != other.pages:
            return False

        return True

    def __repr__(self):
        return (
            "{self.__class__.__name__}("
            "url={self.url}, "
            "pages={self.pages}"
            ")"
        ).format(self=self)

    @property
    def pages(self) -> List[SitemapPage]:
        """
        Return list of pages found in a sitemap.

        :return: List of pages found in a sitemap.
        """
        with open(self.__pages_temp_file_path, 'rb') as tmp:
            pages = pickle.load(tmp)
        return pages

    def all_pages(self) -> Iterator[SitemapPage]:
        """
        Return iterator which yields all pages of this sitemap and linked sitemaps (if any).

        :return: Iterator which yields all pages of this sitemap and linked sitemaps (if any).
        """
        for page in self.pages:
            yield page


class PagesXMLSitemap(AbstractPagesSitemap):
    """
    XML sitemap that contains URLs to pages.
    """
    pass


class PagesTextSitemap(AbstractPagesSitemap):
    """
    Plain text sitemap that contains URLs to pages.
    """
    pass


class PagesRSSSitemap(AbstractPagesSitemap):
    """
    RSS 2.0 sitemap that contains URLs to pages.
    """
    pass


class PagesAtomSitemap(AbstractPagesSitemap):
    """
    RSS 0.3 / 1.0 sitemap that contains URLs to pages.
    """
    pass


class AbstractIndexSitemap(AbstractSitemap):
    """
    Abstract sitemap with URLs to other sitemaps.
    """

    __slots__ = [
        '__sub_sitemaps',
    ]

    def __init__(self, url: str, sub_sitemaps: List[AbstractSitemap]):
        """
        Initialize index sitemap.

        :param url: Sitemap URL.
        :param sub_sitemaps: Sub-sitemaps that are linked to from this sitemap.
        """
        super().__init__(url=url)
        self.__sub_sitemaps = sub_sitemaps

    def __eq__(self, other) -> bool:
        if not isinstance(other, AbstractIndexSitemap):
            raise NotImplemented

        if self.url != other.url:
            return False

        if self.sub_sitemaps != other.sub_sitemaps:
            return False

        return True

    def __repr__(self):
        return (
            "{self.__class__.__name__}("
            "url={self.url}, "
            "sub_sitemaps={self.sub_sitemaps}"
            ")"
        ).format(self=self)

    @property
    def sub_sitemaps(self) -> List[AbstractSitemap]:
        """
        Return sub-sitemaps that are linked to from this sitemap.

        :return: Sub-sitemaps that are linked to from this sitemap.
        """
        return self.__sub_sitemaps

    def all_pages(self) -> Iterator[SitemapPage]:
        """
        Return iterator which yields all pages of this sitemap and linked sitemaps (if any).

        :return: Iterator which yields all pages of this sitemap and linked sitemaps (if any).
        """
        for sub_sitemap in self.sub_sitemaps:
            for page in sub_sitemap.all_pages():
                yield page


class IndexWebsiteSitemap(AbstractIndexSitemap):
    """
    Website's root sitemaps, including robots.txt and extra ones.
    """
    pass


class IndexXMLSitemap(AbstractIndexSitemap):
    """
    XML sitemap with URLs to other sitemaps.
    """
    pass


class IndexRobotsTxtSitemap(AbstractIndexSitemap):
    """
    robots.txt sitemap with URLs to other sitemaps.
    """
    pass
