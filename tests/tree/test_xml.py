import textwrap

from tests.tree.base import TreeTestBase
from usp.objects.page import (
    SitemapPage,
)
from usp.objects.sitemap import (
    IndexRobotsTxtSitemap,
    IndexWebsiteSitemap,
    PagesXMLSitemap,
)
from usp.tree import sitemap_tree_for_homepage


class TestTreeXML(TreeTestBase):
    def test_sitemap_tree_for_homepage_prematurely_ending_xml(self, requests_mock):
        """Test sitemap_tree_for_homepage() with clipped XML.

        Some webservers are misconfigured to limit the request length to a certain number of seconds, in which time the
        server is unable to generate and compress a 50 MB sitemap XML. Google News doesn't seem to have a problem with
        this behavior, so we have to support this too.
        """

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

                Sitemap: {self.TEST_BASE_URL}/sitemap.xml
            """
            ).strip(),
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
                    <url>
                        <loc>{self.TEST_BASE_URL}/news/second.html</loc>
                        <news:news>
                            <news:publication>
                                <news:name>{self.TEST_PUBLICATION_NAME}</news:name>
                                <news:language>{self.TEST_PUBLICATION_LANGUAGE}</news:language>
                            </news:publication>
                            <news:publication_date>{self.TEST_DATE_STR_ISO8601}</news:publication_date>
                            <news:title>Second story</news:title>
                        </news:news>
                    </url>

                    <!-- The following story shouldn't get added as the XML ends prematurely -->
                    <url>
                        <loc>{self.TEST_BASE_URL}/news/third.html</loc>
                        <news:news>
                            <news:publication>
                                <news:name>{self.TEST_PUBLICATION_NAME}</news:name>
                                <news:language>{self.TEST_PUBLICATION_LANGUAGE}</news:language>
                            </news:publication>
                            <news:publicat
            """
            ).strip(),
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        assert isinstance(actual_sitemap_tree, IndexWebsiteSitemap)
        assert len(actual_sitemap_tree.sub_sitemaps) == 1

        assert isinstance(actual_sitemap_tree.sub_sitemaps[0], IndexRobotsTxtSitemap)
        # noinspection PyUnresolvedReferences
        assert len(actual_sitemap_tree.sub_sitemaps[0].sub_sitemaps) == 1

        # noinspection PyUnresolvedReferences
        sitemap = actual_sitemap_tree.sub_sitemaps[0].sub_sitemaps[0]
        assert isinstance(sitemap, PagesXMLSitemap)
        assert len(sitemap.pages) == 2

    def test_sitemap_tree_for_homepage_no_sitemap(self, requests_mock):
        """Test sitemap_tree_for_homepage() with no sitemaps listed in robots.txt."""

        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

        requests_mock.get(
            self.TEST_BASE_URL + "/",
            text="This is a homepage.",
        )

        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
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

    def test_sitemap_tree_for_homepage_unpublished_sitemap(self, requests_mock):
        """Test sitemap_tree_for_homepage() with some sitemaps not published in robots.txt."""

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

                Sitemap: {self.TEST_BASE_URL}/sitemap_public.xml
            """
            ).strip(),
        )

        # Public sitemap (linked to from robots.txt)
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_public.xml",
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                    <url>
                        <loc>{self.TEST_BASE_URL}/news/public.html</loc>
                    </url>
                </urlset>
            """
            ).strip(),
        )

        # Private sitemap (to be discovered by trying out a few paths)
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_index.xml",
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                    <url>
                        <loc>{self.TEST_BASE_URL}/news/private.html</loc>
                    </url>
                </urlset>
            """
            ).strip(),
        )

        expected_sitemap_tree = IndexWebsiteSitemap(
            url=f"{self.TEST_BASE_URL}/",
            sub_sitemaps=[
                IndexRobotsTxtSitemap(
                    url=f"{self.TEST_BASE_URL}/robots.txt",
                    sub_sitemaps=[
                        PagesXMLSitemap(
                            url=f"{self.TEST_BASE_URL}/sitemap_public.xml",
                            pages=[
                                SitemapPage(
                                    url=f"{self.TEST_BASE_URL}/news/public.html",
                                ),
                            ],
                        ),
                    ],
                ),
                PagesXMLSitemap(
                    url=f"{self.TEST_BASE_URL}/sitemap_index.xml",
                    pages=[
                        SitemapPage(
                            url=f"{self.TEST_BASE_URL}/news/private.html",
                        ),
                    ],
                ),
            ],
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        assert expected_sitemap_tree == actual_sitemap_tree
