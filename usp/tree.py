"""Function to generate a sitemap tree."""
from typing import Optional

from usp.web_client.abstract_client import AbstractWebClient
from .exceptions import SitemapException
from .fetchers import SitemapFetcher
from .helpers import is_http_url, strip_url_to_homepage
from .log import create_logger
from .objects import AbstractSitemap

log = create_logger(__name__)


def sitemap_tree_for_homepage(homepage_url: str, web_client: Optional[AbstractWebClient] = None) -> AbstractSitemap:
    """Using a homepage URL, fetch the tree of sitemaps and its stories."""

    if not is_http_url(homepage_url):
        raise SitemapException("URL {} is not a HTTP(s) URL.".format(homepage_url))

    stripped_homepage_url = strip_url_to_homepage(url=homepage_url)
    if homepage_url != stripped_homepage_url:
        log.warning("Assuming that the homepage of {} is {}".format(homepage_url, stripped_homepage_url))
        homepage_url = stripped_homepage_url

    if not homepage_url.endswith('/'):
        homepage_url += '/'
    robots_txt_url = homepage_url + 'robots.txt'

    robots_txt_fetcher = SitemapFetcher(url=robots_txt_url, web_client=web_client, recursion_level=0)
    sitemap_tree = robots_txt_fetcher.sitemap()
    return sitemap_tree
