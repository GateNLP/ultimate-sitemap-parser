"""Objects that represent one of the found sitemaps.

.. seealso::

    :doc:`Reference of classes used for each format </reference/formats>`

.. inheritance-diagram:: AbstractSitemap InvalidSitemap AbstractIndexSitemap IndexWebsiteSitemap IndexXMLSitemap IndexRobotsTxtSitemap AbstractPagesSitemap PagesXMLSitemap PagesTextSitemap PagesRSSSitemap PagesAtomSitemap
    :parts: 1
"""

import abc
from functools import lru_cache
import os
import pickle
import tempfile
from typing import List, Iterator, Tuple

from .page import SitemapPage


# TODO: change to functools.cache when dropping py3.8
@lru_cache(maxsize=None)
def _all_slots(target_cls):
    mro = target_cls.__mro__

    # If a child class doesn't declare slots, getattr reports its parents' slots
    # So we need to track the highest class that declared each slot
    last_slot = {}

    for cls in mro:
        attrs = getattr(cls, "__slots__", tuple())
        for attr in attrs:
            last_slot[attr] = cls

    slots = set()
    for attr, cls in last_slot.items():
        # Attrs belonging to parent classes may be mangled
        if cls is not target_cls and attr.startswith("__"):
            attr = "_" + cls.__name__ + attr
        slots.add(attr)

    return slots


class AbstractSitemap(metaclass=abc.ABCMeta):
    """
    Abstract sitemap.
    """

    __slots__ = [
        "__url",
    ]

    def __init__(self, url: str):
        """
        Initialize a new sitemap.

        :param url: Sitemap URL.
        """
        self.__url = url

    def __eq__(self, other) -> bool:
        if not isinstance(other, AbstractSitemap):
            raise NotImplementedError

        if self.url != other.url:
            return False

        return True

    def __hash__(self):
        return hash((self.url,))

    def __repr__(self):
        return f"{self.__class__.__name__}(" f"url={self.url}" ")"

    @property
    def url(self) -> str:
        """
        Return sitemap URL.

        :return: Sitemap URL.
        """
        return self.__url

    def to_dict(self, with_pages=True) -> dict:
        """
        Return a dictionary representation of the sitemap, including its child sitemaps and optionally pages

        :param with_pages: Include pages in the representation of this sitemap or descendants.
        :return: Dictionary representation of the sitemap.
        """

        return {
            "url": self.url,
        }

    @property
    @abc.abstractmethod
    def pages(self) -> List[SitemapPage]:
        """
        Return a list of pages found in a sitemap (if any).

        Should return an empty list if this sitemap cannot have sub-pages, to allow traversal with a consistent interface.

        :return: the list of pages, or an empty list.
        """
        raise NotImplementedError("Abstract method")

    # TODO: return custom iterator with set length here?
    def all_pages(self) -> Iterator[SitemapPage]:
        """
        Return iterator which yields all pages of this sitemap and linked sitemaps (if any).

        :return: Iterator which yields all pages of this sitemap and linked sitemaps (if any).
        """
        yield from self.pages

    @property
    @abc.abstractmethod
    def sub_sitemaps(self) -> List["AbstractSitemap"]:
        """
        Return a list of sub-sitemaps of this sitemap (if any).

        Should return an empty list if this sitemap cannot have sub-pages, to allow traversal with a consistent interface.

        :return: the list of sub-sitemaps, or an empty list.
        """
        raise NotImplementedError("Abstract method")

    def all_sitemaps(self) -> Iterator["AbstractSitemap"]:
        """
        Return iterator which yields all sub-sitemaps descended from this sitemap.

        :return: Iterator which yields all sub-sitemaps descended from this sitemap.
        """
        yield from self.sub_sitemaps


class InvalidSitemap(AbstractSitemap):
    """Invalid sitemap, e.g. the one that can't be parsed."""

    __slots__ = [
        "__reason",
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
            raise NotImplementedError

        if self.url != other.url:
            return False

        if self.reason != other.reason:
            return False

        return True

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"url={self.url}, "
            f"reason={self.reason}"
            ")"
        )

    def to_dict(self, with_pages=True) -> dict:
        return {
            **super().to_dict(with_pages=with_pages),
            "reason": self.reason,
        }

    @property
    def reason(self) -> str:
        """
        Return reason why the sitemap is deemed invalid.

        :return: Reason why the sitemap is deemed invalid.
        """
        return self.__reason

    @property
    def pages(self) -> List[SitemapPage]:
        """
        Return an empty list of pages, as invalid sitemaps have no pages.

        :return: Empty list of pages.
        """
        return []

    @property
    def sub_sitemaps(self) -> List["AbstractSitemap"]:
        """
        Return an empty list of sub-sitemaps, as invalid sitemaps have no sub-sitemaps.

        :return: Empty list of sub-sitemaps.
        """
        return []


class AbstractPagesSitemap(AbstractSitemap, metaclass=abc.ABCMeta):
    """Abstract sitemap that contains URLs to pages."""

    __slots__ = [
        "__pages_temp_file_path",
    ]

    def __init__(self, url: str, pages: List[SitemapPage]):
        """
        Initialize new pages sitemap.

        :param url: Sitemap URL.
        :param pages: List of pages found in a sitemap.
        """
        super().__init__(url=url)

        self._dump_pages(pages)

    def _dump_pages(self, pages: List[SitemapPage]):
        temp_file, self.__pages_temp_file_path = tempfile.mkstemp()
        with open(self.__pages_temp_file_path, "wb") as tmp:
            pickle.dump(pages, tmp, protocol=pickle.HIGHEST_PROTOCOL)

    def __del__(self):
        os.unlink(self.__pages_temp_file_path)

    def __eq__(self, other) -> bool:
        if not isinstance(other, AbstractPagesSitemap):
            raise NotImplementedError

        if self.url != other.url:
            return False

        if self.pages != other.pages:
            return False

        return True

    def __repr__(self):
        return f"{self.__class__.__name__}(url={self.url}, pages={self.pages})"

    def __getstate__(self) -> Tuple[None, dict]:
        # Load slots of this class and its parents (mangling if appropriate)
        obj_slots = {slot: getattr(self, slot) for slot in _all_slots(self.__class__)}
        # Replace temp file path with actual content
        del obj_slots["_AbstractPagesSitemap__pages_temp_file_path"]
        obj_slots["_pages_value"] = self.pages
        return None, obj_slots

    def __setstate__(self, state: tuple):
        _, attrs = state
        # We can't restore contents without this key
        if "_pages_value" not in attrs:
            raise ValueError("State does not contain pages value")
        pages_val = attrs.pop("_pages_value")
        for slot, val in attrs.items():
            setattr(self, slot, val)
        self._dump_pages(pages_val)

    def to_dict(self, with_pages=True) -> dict:
        obj = {
            **super().to_dict(with_pages=with_pages),
        }

        if with_pages:
            obj["pages"] = [page.to_dict() for page in self.pages]

        return obj

    @property
    def pages(self) -> List[SitemapPage]:
        """
        Load pages from disk swap file and return them.

        :return: List of pages found in the sitemap.
        """
        with open(self.__pages_temp_file_path, "rb") as tmp:
            pages = pickle.load(tmp)
        return pages

    @property
    def sub_sitemaps(self) -> List["AbstractSitemap"]:
        """
        Return an empty list of sub-sitemaps, as pages sitemaps have no sub-sitemaps.

        :return: Empty list of sub-sitemaps.
        """
        return []


# TODO: declare empty __slots__
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
        "__sub_sitemaps",
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
            raise NotImplementedError

        if self.url != other.url:
            return False

        if self.sub_sitemaps != other.sub_sitemaps:
            return False

        return True

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"url={self.url}, "
            f"sub_sitemaps={self.sub_sitemaps}"
            ")"
        )

    def to_dict(self, with_pages=True) -> dict:
        return {
            **super().to_dict(with_pages=with_pages),
            "sub_sitemaps": [
                sub_sitemap.to_dict(with_pages=with_pages)
                for sub_sitemap in self.sub_sitemaps
            ],
        }

    @property
    def sub_sitemaps(self) -> List["AbstractSitemap"]:
        return self.__sub_sitemaps

    @property
    def pages(self) -> List[SitemapPage]:
        """
        Return an empty list of pages, as index sitemaps have no pages.

        :return: Empty list of pages.
        """
        return []

    def all_pages(self) -> Iterator[SitemapPage]:
        """
        Return iterator which yields all pages of this sitemap and linked sitemaps (if any).

        :return: Iterator which yields all pages of this sitemap and linked sitemaps (if any).
        """
        for sub_sitemap in self.sub_sitemaps:
            yield from sub_sitemap.all_pages()

    def all_sitemaps(self) -> Iterator["AbstractSitemap"]:
        """
        Return iterator which yields all sub-sitemaps of this sitemap.

        :return: Iterator which yields all sub-sitemaps of this sitemap.
        """
        for sub_sitemap in self.sub_sitemaps:
            yield sub_sitemap
            yield from sub_sitemap.all_sitemaps()


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
