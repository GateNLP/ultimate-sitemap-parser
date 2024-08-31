import difflib
import textwrap

from tests.helpers import gzip
from tests.tree.base import TreeTestBase
from usp.tree import sitemap_tree_for_homepage

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

class TestTreeRobots(TreeTestBase):
    def test_sitemap_tree_for_homepage_robots_txt_no_content_type(self, requests_mock):
        """Test sitemap_tree_for_homepage() with no Content-Type in robots.txt."""

        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

        requests_mock.get(
            self.TEST_BASE_URL + "/",
            text="This is a homepage.",
        )

        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": ""},
            text=textwrap.dedent(
                """
                User-agent: *
                Disallow: /whatever
            """.format()
            ).strip(),
        )

        expected_sitemap_tree = IndexWebsiteSitemap(
            url=f"{self.TEST_BASE_URL}/",
            sub_sitemaps=[
                IndexRobotsTxtSitemap(
                    url=f"{self.TEST_BASE_URL}/robots.txt",
                    sub_sitemaps=[],
                )
            ],
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        assert expected_sitemap_tree == actual_sitemap_tree

    def test_sitemap_tree_for_homepage_no_robots_txt(self, requests_mock):
        """Test sitemap_tree_for_homepage() with no robots.txt."""

        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

        requests_mock.get(
            self.TEST_BASE_URL + "/",
            text="This is a homepage.",
        )

        # Nonexistent robots.txt
        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            status_code=404,
            reason="Not Found",
            headers={"Content-Type": "text/html"},
            text="<h1>404 Not Found!</h1>",
        )

        expected_sitemap_tree = IndexWebsiteSitemap(
            url=f"{self.TEST_BASE_URL}/",
            sub_sitemaps=[],
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        assert expected_sitemap_tree == actual_sitemap_tree

    def test_sitemap_tree_for_homepage_robots_txt_weird_spacing(self, requests_mock):
        """Test sitemap_tree_for_homepage() with weird (but valid) spacing."""

        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

        requests_mock.get(
            self.TEST_BASE_URL + "/",
            text="This is a homepage.",
        )

        robots_txt_body = ""
        robots_txt_body += "User-agent: *\n"
        # Extra space before "Sitemap:", no space after "Sitemap:", and extra space after sitemap URL
        robots_txt_body += f" Sitemap:{self.TEST_BASE_URL}/sitemap.xml    "

        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
            text=robots_txt_body,
        )

        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap.xml",
            text=textwrap.dedent(
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
            ).strip(),
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)
        assert len(list(actual_sitemap_tree.all_pages())) == 1
        assert len(list(actual_sitemap_tree.all_sitemaps())) == 2
