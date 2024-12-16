"""Objects that represent a page found in one of the sitemaps."""

import datetime
from decimal import Decimal
from enum import Enum, unique
from typing import List, Optional

SITEMAP_PAGE_DEFAULT_PRIORITY = Decimal("0.5")
"""Default sitemap page priority, as per the spec."""


class SitemapNewsStory:
    """
    Single story derived from Google News XML sitemap.
    """

    __slots__ = [
        "__title",
        "__publish_date",
        "__publication_name",
        "__publication_language",
        "__access",
        "__genres",
        "__keywords",
        "__stock_tickers",
    ]

    def __init__(
        self,
        title: str,
        publish_date: datetime.datetime,
        publication_name: Optional[str] = None,
        publication_language: Optional[str] = None,
        access: Optional[str] = None,
        genres: List[str] = None,
        keywords: List[str] = None,
        stock_tickers: List[str] = None,
    ):
        """
        Initialize a new Google News story.

        :param title: Story title.
        :param publish_date: Story publication date.
        :param publication_name: Name of the news publication in which the article appears in.
        :param publication_language: Primary language of the news publication in which the article appears in.
        :param access: Accessibility of the article.
        :param genres: List of properties characterizing the content of the article.
        :param keywords: List of keywords describing the topic of the article.
        :param stock_tickers: List of up to 5 stock tickers that are the main subject of the article.
        """

        # Spec defines that some of the properties below are "required" but in practice not every website provides the
        # required properties. So, we require only "title" and "publish_date" to be set.

        self.__title = title
        self.__publish_date = publish_date
        self.__publication_name = publication_name
        self.__publication_language = publication_language
        self.__access = access
        self.__genres = genres if genres else []
        self.__keywords = keywords if keywords else []
        self.__stock_tickers = stock_tickers if stock_tickers else []

    def __eq__(self, other) -> bool:
        """Check equality."""
        if not isinstance(other, SitemapNewsStory):
            raise NotImplementedError

        if self.title != other.title:
            return False

        if self.publish_date != other.publish_date:
            return False

        if self.publication_name != other.publication_name:
            return False

        if self.publication_language != other.publication_language:
            return False

        if self.access != other.access:
            return False

        if self.genres != other.genres:
            return False

        if self.keywords != other.keywords:
            return False

        if self.stock_tickers != other.stock_tickers:
            return False

        return True

    def to_dict(self) -> dict:
        """
        Convert to a dictionary representation.

        :return: the news story data as a dictionary
        """
        return {
            "title": self.title,
            "publish_date": self.publish_date,
            "publication_name": self.publication_name,
            "publication_language": self.publication_language,
            "access": self.access,
            "genres": self.genres,
            "keywords": self.keywords,
            "stock_tickers": self.stock_tickers,
        }

    def __hash__(self):
        return hash(
            (
                self.title,
                self.publish_date,
                self.publication_name,
                self.publication_language,
                self.access,
                self.genres,
                self.keywords,
                self.stock_tickers,
            )
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"title={self.title}, "
            f"publish_date={self.publish_date}, "
            f"publication_name={self.publication_name}, "
            f"publication_language={self.publication_language}, "
            f"access={self.access}, "
            f"genres={self.genres}, "
            f"keywords={self.keywords}, "
            f"stock_tickers={self.stock_tickers}"
            ")"
        )

    @property
    def title(self) -> str:
        """Get the story title."""
        return self.__title

    @property
    def publish_date(self) -> datetime.datetime:
        """Get the  story publication date."""
        return self.__publish_date

    @property
    def publication_name(self) -> Optional[str]:
        """Get the name of the news publication in which the article appears."""
        return self.__publication_name

    @property
    def publication_language(self) -> Optional[str]:
        """Get the primary language of the news publication in which the article appears.

        It should be an ISO 639 Language Code (either 2 or 3 letters).
        """
        return self.__publication_language

    @property
    def access(self) -> Optional[str]:
        """Get the accessibility of the article.

        :return: Accessibility of the article.
        """
        return self.__access

    @property
    def genres(self) -> List[str]:
        """Get list of genres characterizing the content of the article.

        Genres will be one "PressRelease", "Satire", "Blog", "OpEd", "Opinion", "UserGenerated"
        """
        return self.__genres

    @property
    def keywords(self) -> List[str]:
        """Get list of keywords describing the topic of the article."""
        return self.__keywords

    @property
    def stock_tickers(self) -> List[str]:
        """Get stock tickers that are the main subject of the article.

        Each ticker must be prefixed by the name of its stock exchange, and must match its entry in Google Finance.
        For example, "NASDAQ:AMAT" (but not "NASD:AMAT"), or "BOM:500325" (but not "BOM:RIL").

        Up to 5 tickers can be provided.
        """
        return self.__stock_tickers


class SitemapImage:
    """
    Single image derived from Google Image XML sitemap.

    All properties except ``loc`` are now deprecated in the XML specification, see
    https://developers.google.com/search/blog/2022/05/spring-cleaning-sitemap-extensions

    They will continue to be supported here.
    """

    __slots__ = ["__loc", "__caption", "__geo_location", "__title", "__license"]

    def __init__(
        self,
        loc: str,
        caption: Optional[str] = None,
        geo_location: Optional[str] = None,
        title: Optional[str] = None,
        license_: Optional[str] = None,
    ):
        """Initialise a Google Image.

        :param loc: the URL of the image
        :param caption: the caption of the image, optional
        :param geo_location: the geographic location of the image, for example "Limerick, Ireland", optional
        :param title: the title of the image, optional
        :param license_: a URL to the license of the image, optional
        """
        self.__loc = loc
        self.__caption = caption
        self.__geo_location = geo_location
        self.__title = title
        self.__license = license_

    def __eq__(self, other) -> bool:
        if not isinstance(other, SitemapImage):
            raise NotImplementedError

        if self.loc != other.loc:
            return False

        if self.caption != other.caption:
            return False

        if self.geo_location != other.geo_location:
            return False

        if self.title != other.title:
            return False

        if self.license != other.license:
            return False

        return True

    def to_dict(self):
        """Convert to a dictionary representation.

        :return: the image data as a dictionary
        """
        return {
            "loc": self.loc,
            "caption": self.caption,
            "geo_location": self.geo_location,
            "title": self.title,
            "license": self.license,
        }

    def __hash__(self):
        return hash(
            (self.loc, self.caption, self.geo_location, self.title, self.license)
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"loc={self.loc}, "
            f"caption={self.caption}, "
            f"geo_location={self.geo_location}, "
            f"title={self.title}, "
            f"license={self.license}"
            ")"
        )

    @property
    def loc(self) -> str:
        """Get the URL of the image."""
        return self.__loc

    @property
    def caption(self) -> Optional[str]:
        """Get the caption of the image."""
        return self.__caption

    @property
    def geo_location(self) -> Optional[str]:
        """Get the geographic location of the image."""
        return self.__geo_location

    @property
    def title(self) -> Optional[str]:
        """Get the title of the image."""
        return self.__title

    @property
    def license(self) -> Optional[str]:
        """Get a URL to the license of the image."""
        return self.__license


@unique
class SitemapPageChangeFrequency(Enum):
    """Change frequency of a sitemap URL."""

    ALWAYS = "always"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    NEVER = "never"

    @classmethod
    def has_value(cls, value: str) -> bool:
        """Test if enum has specified value."""
        return any(value == item.value for item in cls)


class SitemapPage:
    """Single sitemap-derived page."""

    __slots__ = [
        "__url",
        "__priority",
        "__last_modified",
        "__change_frequency",
        "__news_story",
        "__images",
    ]

    def __init__(
        self,
        url: str,
        priority: Decimal = SITEMAP_PAGE_DEFAULT_PRIORITY,
        last_modified: Optional[datetime.datetime] = None,
        change_frequency: Optional[SitemapPageChangeFrequency] = None,
        news_story: Optional[SitemapNewsStory] = None,
        images: Optional[List[SitemapImage]] = None,
    ):
        """
        Initialize a new sitemap-derived page.

        :param url: Page URL.
        :param priority: Priority of this URL relative to other URLs on your site.
        :param last_modified: Date of last modification of the URL.
        :param change_frequency: Change frequency of a sitemap URL.
        :param news_story: Google News story attached to the URL.
        """
        self.__url = url
        self.__priority = priority
        self.__last_modified = last_modified
        self.__change_frequency = change_frequency
        self.__news_story = news_story
        self.__images = images

    def __eq__(self, other) -> bool:
        if not isinstance(other, SitemapPage):
            raise NotImplementedError

        if self.url != other.url:
            return False

        if self.priority != other.priority:
            return False

        if self.last_modified != other.last_modified:
            return False

        if self.change_frequency != other.change_frequency:
            return False

        if self.news_story != other.news_story:
            return False

        if self.images != other.images:
            return False

        return True

    def __hash__(self):
        return hash(
            (
                # Hash only the URL to be able to find unique pages later on
                self.url,
            )
        )

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"url={self.url}, "
            f"priority={self.priority}, "
            f"last_modified={self.last_modified}, "
            f"change_frequency={self.change_frequency}, "
            f"news_story={self.news_story}, "
            f"images={self.images}"
            ")"
        )

    def to_dict(self):
        """
        Convert this page to a dictionary.
        """

        return {
            "url": self.url,
            "priority": self.priority,
            "last_modified": self.last_modified,
            "change_frequency": self.change_frequency.value
            if self.change_frequency
            else None,
            "news_story": self.news_story.to_dict() if self.news_story else None,
            "images": [image.to_dict() for image in self.images]
            if self.images
            else None,
        }

    @property
    def url(self) -> str:
        """Get the page URL."""
        return self.__url

    @property
    def priority(self) -> Decimal:
        """Get the priority of this URL relative to other URLs on the site."""
        return self.__priority

    @property
    def last_modified(self) -> Optional[datetime.datetime]:
        """Get the date of last modification of the URL."""
        return self.__last_modified

    @property
    def change_frequency(self) -> Optional[SitemapPageChangeFrequency]:
        """Get the change frequency of a sitemap URL."""
        return self.__change_frequency

    @property
    def news_story(self) -> Optional[SitemapNewsStory]:
        """Get the Google News story attached to the URL."""
        return self.__news_story

    @property
    def images(self) -> Optional[List[SitemapImage]]:
        """Get the images attached to the URL."""
        return self.__images
