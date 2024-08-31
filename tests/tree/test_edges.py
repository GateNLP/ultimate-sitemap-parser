from decimal import Decimal
import difflib
import textwrap
from tests.helpers import gzip


from tests.tree.base import TreeTestBase

from usp.objects.sitemap import (
    IndexRobotsTxtSitemap,
    PagesXMLSitemap,
    IndexXMLSitemap,
    InvalidSitemap,
    PagesTextSitemap,
    IndexWebsiteSitemap,
    PagesRSSSitemap,
    PagesAtomSitemap,
)

from usp.objects.page import (
    SitemapPage,
    SitemapNewsStory,
    SitemapPageChangeFrequency,
)
from usp.tree import sitemap_tree_for_homepage


class TestTreeBasic(TreeTestBase):
    def test_sitemap_tree_for_homepage_utf8_bom(self, requests_mock):
        """Test sitemap_tree_for_homepage() with UTF-8 BOM in both robots.txt and sitemap."""

        robots_txt_body = textwrap.dedent(
            f"""
            User-agent: *
            Disallow: /whatever

            Sitemap: {self.TEST_BASE_URL}/sitemap.xml
        """
        ).strip()

        sitemap_xml_body = textwrap.dedent(
            f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                    xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
                <url>
                    <loc>{self.TEST_BASE_URL}/news/first.html</loc>
                    <news:news>
                        <news:publication>
                            <news:name>{self.TEST_PUBLICATION_NAME}</news:name>
                            <news:language>{self.TEST_PUBLICATION_LANGUAGE}</news:language>
                        </news:publication>
                        <news:publication_date>{self.TEST_DATE_STR_ISO8601}</news:publication_date>
                        <news:title>First story</news:title>
                    </news:news>
                </url>
            </urlset>
        """
        ).strip()

        robots_txt_body_encoded = robots_txt_body.encode("utf-8-sig")
        sitemap_xml_body_encoded = sitemap_xml_body.encode("utf-8-sig")

        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

        requests_mock.get(
            self.TEST_BASE_URL + "/",
            text="This is a homepage.",
        )

        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
            content=robots_txt_body_encoded,
        )

        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap.xml",
            content=sitemap_xml_body_encoded,
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)
        assert len(list(actual_sitemap_tree.all_pages())) == 1
        assert len(list(actual_sitemap_tree.all_sitemaps())) == 2

    def test_max_recursion_level_xml(self, requests_mock):
        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)
        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
            text=(textwrap.dedent(
                f"""
            User-agent: *
            Disallow: /whatever

            Sitemap: {self.TEST_BASE_URL}/sitemap.xml
        """
            ).strip()),
        )
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap.xml",
            headers={"Content-Type": "application/xml"},
            text=(textwrap.dedent(
                f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                <sitemap>
                    <loc>{self.TEST_BASE_URL}/sitemap.xml</loc>
                    <lastmod>2024-01-01</lastmod>
                </sitemap>
            </sitemapindex>
            """
            ).strip()),
        )

        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)
        sitemaps = list(tree.all_sitemaps())

        assert type(sitemaps[-1]) is InvalidSitemap


    def test_max_recursion_level_robots(self, requests_mock):
        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)
        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
            text=(textwrap.dedent(
                f"""
            User-agent: *
            Disallow: /whatever

            Sitemap: {self.TEST_BASE_URL}/robots.txt
        """
            ).strip()),
        )
        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)
        sitemaps = list(tree.all_sitemaps())
        assert type(sitemaps[-1]) is InvalidSitemap
