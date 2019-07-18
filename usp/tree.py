"""Helpers to generate a sitemap tree."""

from typing import Optional

from .exceptions import SitemapException
from .fetch_parse import SitemapFetcher
from .helpers import is_http_url, strip_url_to_homepage
from .log import create_logger
from .objects.sitemap import AbstractSitemap, InvalidSitemap, IndexWebsiteSitemap, IndexRobotsTxtSitemap
from .web_client.abstract_client import AbstractWebClient

log = create_logger(__name__)

_UNPUBLISHED_SITEMAP_PATHS = {
    'sitemap.xml',
    'sitemap.xml.gz',
    'sitemap_index.xml',
    'sitemap-index.xml',
    'sitemap_index.xml.gz',
    'sitemap-index.xml.gz',
    '.sitemap.xml',
    'sitemap',
    'admin/config/search/xmlsitemap',
    'sitemap/sitemap-index.xml',
}
"""Paths which are not exposed in robots.txt but might still contain a sitemap."""


def sitemap_tree_for_homepage(homepage_url: str, web_client: Optional[AbstractWebClient] = None) -> AbstractSitemap:
    """
    Using a homepage URL, fetch the tree of sitemaps and pages listed in them.

    :param homepage_url: Homepage URL of a website to fetch the sitemap tree for, e.g. "http://www.example.com/".
    :param web_client: Web client implementation to use for fetching sitemaps.
    :return: Root sitemap object of the fetched sitemap tree.
    """

    if not is_http_url(homepage_url):
        raise SitemapException("URL {} is not a HTTP(s) URL.".format(homepage_url))

    stripped_homepage_url = strip_url_to_homepage(url=homepage_url)
    if homepage_url != stripped_homepage_url:
        log.warning("Assuming that the homepage of {} is {}".format(homepage_url, stripped_homepage_url))
        homepage_url = stripped_homepage_url

    if not homepage_url.endswith('/'):
        homepage_url += '/'
    robots_txt_url = homepage_url + 'robots.txt'

    sitemaps = []

    robots_txt_fetcher = SitemapFetcher(url=robots_txt_url, web_client=web_client, recursion_level=0)
    robots_txt_sitemap = robots_txt_fetcher.sitemap()
    sitemaps.append(robots_txt_sitemap)

    sitemap_urls_found_in_robots_txt = set()
    if isinstance(robots_txt_sitemap, IndexRobotsTxtSitemap):
        for sub_sitemap in robots_txt_sitemap.sub_sitemaps:
            sitemap_urls_found_in_robots_txt.add(sub_sitemap.url)

    for unpublished_sitemap_path in _UNPUBLISHED_SITEMAP_PATHS:
        unpublished_sitemap_url = homepage_url + unpublished_sitemap_path

        # Don't refetch URLs already found in robots.txt
        if unpublished_sitemap_url not in sitemap_urls_found_in_robots_txt:

            unpublished_sitemap_fetcher = SitemapFetcher(
                url=unpublished_sitemap_url,
                web_client=web_client,
                recursion_level=0,
            )
            unpublished_sitemap = unpublished_sitemap_fetcher.sitemap()

            # Skip the ones that weren't found
            if not isinstance(unpublished_sitemap, InvalidSitemap):
                sitemaps.append(unpublished_sitemap)

    index_sitemap = IndexWebsiteSitemap(url=homepage_url, sub_sitemaps=sitemaps)

    return index_sitemap
