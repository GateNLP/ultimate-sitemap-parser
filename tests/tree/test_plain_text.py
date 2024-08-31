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

class TestTreeBasic(TreeTestBase):
    def test_sitemap_tree_for_homepage_plain_text(self, requests_mock):
        """Test sitemap_tree_for_homepage() with plain text sitemaps."""

        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

        requests_mock.get(
            self.TEST_BASE_URL + "/",
            text="This is a homepage.",
        )

        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
            text=textwrap.dedent(
                f"""
                User-agent: *
                Disallow: /whatever

                Sitemap: {self.TEST_BASE_URL}/sitemap_1.txt
                Sitemap: {self.TEST_BASE_URL}/sitemap_2.txt.dat
            """
            ).strip(),
        )

        # Plain text uncompressed sitemap (no Content-Type header)
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_1.txt",
            text=textwrap.dedent(
                f"""

                {self.TEST_BASE_URL}/news/foo.html


                {self.TEST_BASE_URL}/news/bar.html

                Some other stuff which totally doesn't look like an URL
            """
            ).strip(),
        )

        # Plain text compressed sitemap without .gz extension
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_2.txt.dat",
            headers={"Content-Type": "application/x-gzip"},
            content=gzip(
                textwrap.dedent(
                    f"""
                {self.TEST_BASE_URL}/news/bar.html
                    {self.TEST_BASE_URL}/news/baz.html
            """
                ).strip()
            ),
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        assert isinstance(actual_sitemap_tree, IndexWebsiteSitemap)
        assert len(actual_sitemap_tree.sub_sitemaps) == 1

        assert isinstance(actual_sitemap_tree.sub_sitemaps[0], IndexRobotsTxtSitemap)
        # noinspection PyUnresolvedReferences
        assert len(actual_sitemap_tree.sub_sitemaps[0].sub_sitemaps) == 2

        # noinspection PyUnresolvedReferences
        sitemap_1 = actual_sitemap_tree.sub_sitemaps[0].sub_sitemaps[0]
        assert isinstance(sitemap_1, PagesTextSitemap)
        assert len(sitemap_1.pages) == 2

        # noinspection PyUnresolvedReferences
        sitemap_2 = actual_sitemap_tree.sub_sitemaps[0].sub_sitemaps[1]
        assert isinstance(sitemap_2, PagesTextSitemap)
        assert len(sitemap_2.pages) == 2

        pages = list(actual_sitemap_tree.all_pages())
        assert len(pages) == 4
        assert SitemapPage(url=f"{self.TEST_BASE_URL}/news/foo.html") in pages
        assert SitemapPage(url=f"{self.TEST_BASE_URL}/news/bar.html") in pages
        assert SitemapPage(url=f"{self.TEST_BASE_URL}/news/baz.html") in pages

        assert len(list(actual_sitemap_tree.all_sitemaps())) == 3
