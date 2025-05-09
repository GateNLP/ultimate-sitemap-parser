import difflib
import textwrap
from decimal import Decimal

from tests.helpers import gzip
from tests.tree.base import TreeTestBase
from usp.objects.page import (
    SitemapNewsStory,
    SitemapPage,
    SitemapPageChangeFrequency,
)
from usp.objects.sitemap import (
    IndexRobotsTxtSitemap,
    IndexWebsiteSitemap,
    IndexXMLSitemap,
    InvalidSitemap,
    PagesXMLSitemap,
)
from usp.tree import sitemap_tree_for_homepage


class TestTreeBasic(TreeTestBase):
    def test_sitemap_tree_for_homepage(self, requests_mock):
        """Test sitemap_tree_for_homepage()."""
        self.init_basic_sitemap(requests_mock)

        expected_sitemap_tree = IndexWebsiteSitemap(
            url=f"{self.TEST_BASE_URL}/",
            sub_sitemaps=[
                IndexRobotsTxtSitemap(
                    url=f"{self.TEST_BASE_URL}/robots.txt",
                    sub_sitemaps=[
                        PagesXMLSitemap(
                            url=f"{self.TEST_BASE_URL}/sitemap_pages.xml",
                            pages=[
                                SitemapPage(
                                    url=f"{self.TEST_BASE_URL}/about.html",
                                    last_modified=self.TEST_DATE_DATETIME,
                                    news_story=None,
                                    change_frequency=SitemapPageChangeFrequency.MONTHLY,
                                    priority=Decimal("0.8"),
                                ),
                                SitemapPage(
                                    url=f"{self.TEST_BASE_URL}/contact.html",
                                    last_modified=self.TEST_DATE_DATETIME,
                                    news_story=None,
                                    # Invalid input -- should be reset to "always"
                                    change_frequency=SitemapPageChangeFrequency.ALWAYS,
                                    # Invalid input -- should be reset to 0.5 (the default as per the spec)
                                    priority=Decimal("0.5"),
                                ),
                            ],
                        ),
                        IndexXMLSitemap(
                            url=f"{self.TEST_BASE_URL}/sitemap_news_index_1.xml",
                            sub_sitemaps=[
                                PagesXMLSitemap(
                                    url=f"{self.TEST_BASE_URL}/sitemap_news_1.xml",
                                    pages=[
                                        SitemapPage(
                                            url=f"{self.TEST_BASE_URL}/news/foo.html",
                                            news_story=SitemapNewsStory(
                                                title="Foo <foo>",
                                                publish_date=self.TEST_DATE_DATETIME,
                                                publication_name=self.TEST_PUBLICATION_NAME,
                                                publication_language=self.TEST_PUBLICATION_LANGUAGE,
                                            ),
                                        ),
                                        SitemapPage(
                                            url=f"{self.TEST_BASE_URL}/news/bar.html",
                                            news_story=SitemapNewsStory(
                                                title="Bar & bar",
                                                publish_date=self.TEST_DATE_DATETIME,
                                                publication_name=self.TEST_PUBLICATION_NAME,
                                                publication_language=self.TEST_PUBLICATION_LANGUAGE,
                                            ),
                                        ),
                                    ],
                                ),
                                IndexXMLSitemap(
                                    url=f"{self.TEST_BASE_URL}/sitemap_news_index_2.xml",
                                    sub_sitemaps=[
                                        PagesXMLSitemap(
                                            url=f"{self.TEST_BASE_URL}/sitemap_news_2.xml",
                                            pages=[
                                                SitemapPage(
                                                    url=f"{self.TEST_BASE_URL}/news/bar.html",
                                                    news_story=SitemapNewsStory(
                                                        title="Bar & bar",
                                                        publish_date=self.TEST_DATE_DATETIME,
                                                        publication_name=self.TEST_PUBLICATION_NAME,
                                                        publication_language=self.TEST_PUBLICATION_LANGUAGE,
                                                    ),
                                                ),
                                                SitemapPage(
                                                    url=f"{self.TEST_BASE_URL}/news/baz.html",
                                                    news_story=SitemapNewsStory(
                                                        title="Bąž",
                                                        publish_date=self.TEST_DATE_DATETIME,
                                                        publication_name=self.TEST_PUBLICATION_NAME,
                                                        publication_language=self.TEST_PUBLICATION_LANGUAGE,
                                                    ),
                                                ),
                                            ],
                                        ),
                                        InvalidSitemap(
                                            url=f"{self.TEST_BASE_URL}/sitemap_news_missing.xml",
                                            reason=(
                                                f"Unable to fetch sitemap from {self.TEST_BASE_URL}/sitemap_news_missing.xml: "
                                                "404 Not Found"
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                )
            ],
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        expected_lines = str(expected_sitemap_tree).split()
        actual_lines = str(actual_sitemap_tree).split()
        print(actual_lines)
        diff = difflib.ndiff(expected_lines, actual_lines)
        diff_str = "\n".join(diff)

        assert expected_sitemap_tree == actual_sitemap_tree, diff_str

        assert len(list(actual_sitemap_tree.all_pages())) == 6
        assert len(list(actual_sitemap_tree.all_sitemaps())) == 7

    def test_sitemap_tree_for_homepage_gzip(self, requests_mock, caplog):
        """Test sitemap_tree_for_homepage() with gzipped sitemaps."""

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

                Sitemap: {self.TEST_BASE_URL}/sitemap_1.gz
                Sitemap: {self.TEST_BASE_URL}/sitemap_2.dat
                Sitemap: {self.TEST_BASE_URL}/sitemap_3.xml.gz
                Sitemap: {self.TEST_BASE_URL}/sitemap_4.xml
            """
            ).strip(),
        )

        # Gzipped sitemap without correct HTTP header but with .gz extension
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_1.gz",
            content=gzip(
                textwrap.dedent(
                    f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
                    <url>
                        <loc>{self.TEST_BASE_URL}/news/foo.html</loc>
                        <news:news>
                            <news:publication>
                                <news:name>{self.TEST_PUBLICATION_NAME}</news:name>
                                <news:language>{self.TEST_PUBLICATION_LANGUAGE}</news:language>
                            </news:publication>
                            <news:publication_date>{self.TEST_DATE_STR_ISO8601}</news:publication_date>
                            <news:title>Foo &lt;foo&gt;</news:title>    <!-- HTML entity decoding -->
                        </news:news>
                    </url>
                </urlset>
            """
                ).strip()
            ),
        )

        # Gzipped sitemap with correct HTTP header but without .gz extension
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_2.dat",
            headers={"Content-Type": "application/x-gzip"},
            content=gzip(
                textwrap.dedent(
                    f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
                    <url>
                        <loc>{self.TEST_BASE_URL}/news/bar.html</loc>
                        <news:news>
                            <news:publication>
                                <news:name>{self.TEST_PUBLICATION_NAME}</news:name>
                                <news:language>{self.TEST_PUBLICATION_LANGUAGE}</news:language>
                            </news:publication>
                            <news:publication_date>{self.TEST_DATE_STR_ISO8601}</news:publication_date>
                            <news:title><![CDATA[Bąr]]></news:title>    <!-- CDATA and UTF-8 -->
                        </news:news>
                    </url>
                </urlset>
            """
                ).strip()
            ),
        )

        # Sitemap which appears to be gzipped (due to extension and Content-Type) but really isn't
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_3.xml.gz",
            headers={"Content-Type": "application/x-gzip"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
                    <url>
                        <loc>{self.TEST_BASE_URL}/news/baz.html</loc>
                        <news:news>
                            <news:publication>
                                <news:name>{self.TEST_PUBLICATION_NAME}</news:name>
                                <news:language>{self.TEST_PUBLICATION_LANGUAGE}</news:language>
                            </news:publication>
                            <news:publication_date>{self.TEST_DATE_STR_ISO8601}</news:publication_date>
                            <news:title><![CDATA[Bąž]]></news:title>    <!-- CDATA and UTF-8 -->
                        </news:news>
                    </url>
                </urlset>
            """
            ).strip(),
        )

        # Sitemap encoded as gzip for transport by the web server
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_4.xml",
            headers={"Content-Type": "application/xml", "Content-Encoding": "gzip"},
            content=gzip(
                textwrap.dedent(
                    f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
                    <url>
                        <loc>{self.TEST_BASE_URL}/news/baz.html</loc>
                        <news:news>
                            <news:publication>
                                <news:name>{self.TEST_PUBLICATION_NAME}</news:name>
                                <news:language>{self.TEST_PUBLICATION_LANGUAGE}</news:language>
                            </news:publication>
                            <news:publication_date>{self.TEST_DATE_STR_ISO8601}</news:publication_date>
                            <news:title><![CDATA[Bąž]]></news:title>    <!-- CDATA and UTF-8 -->
                        </news:news>
                    </url>
                </urlset>
            """
                ).strip()
            ),
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        # Don't do an in-depth check, we just need to make sure that gunzip works
        assert isinstance(actual_sitemap_tree, IndexWebsiteSitemap)
        assert len(actual_sitemap_tree.sub_sitemaps) == 1

        assert isinstance(actual_sitemap_tree.sub_sitemaps[0], IndexRobotsTxtSitemap)
        # noinspection PyUnresolvedReferences
        assert len(actual_sitemap_tree.sub_sitemaps[0].sub_sitemaps) == 4

        # noinspection PyUnresolvedReferences
        sitemap_1 = actual_sitemap_tree.sub_sitemaps[0].sub_sitemaps[0]
        assert isinstance(sitemap_1, PagesXMLSitemap)
        assert len(sitemap_1.pages) == 1

        # noinspection PyUnresolvedReferences
        sitemap_2 = actual_sitemap_tree.sub_sitemaps[0].sub_sitemaps[1]
        assert isinstance(sitemap_2, PagesXMLSitemap)
        assert len(sitemap_2.pages) == 1

        # noinspection PyUnresolvedReferences
        sitemap_3 = actual_sitemap_tree.sub_sitemaps[0].sub_sitemaps[2]
        assert isinstance(sitemap_3, PagesXMLSitemap)
        assert len(sitemap_3.pages) == 1

        sitemap_4 = actual_sitemap_tree.sub_sitemaps[0].sub_sitemaps[3]
        assert isinstance(sitemap_4, PagesXMLSitemap)
        assert len(sitemap_4.pages) == 1

        # Check that only sitemap_3 caused a gunzip error
        assert (
            len(
                [
                    record
                    for record in caplog.records
                    if "Unable to gunzip response" in record.message
                ]
            )
            == 1
        )
        assert (
            f"Unable to gunzip response for {self.TEST_BASE_URL}/sitemap_3.xml.gz"
            in caplog.text
        )

    def test_sitemap_tree_for_homepage_huge_sitemap(self, requests_mock):
        """Test sitemap_tree_for_homepage() with a huge sitemap (mostly for profiling)."""

        page_count = 1000

        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                    xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
                    xmlns:xhtml="http://www.w3.org/1999/xhtml">
        """
        for x in range(page_count):
            sitemap_xml += f"""
                <url>
                    <loc>{self.TEST_BASE_URL}/news/page_{x}.html</loc>

                    <!-- Element present but empty -->
                    <lastmod />

                    <!-- Some other XML namespace -->
                    <xhtml:link rel="alternate"
                                media="only screen and (max-width: 640px)"
                                href="{self.TEST_BASE_URL}/news/page_{x}.html?mobile=1" />

                    <news:news>
                        <news:publication>
                            <news:name>{self.TEST_PUBLICATION_NAME}</news:name>
                            <news:language>{self.TEST_PUBLICATION_LANGUAGE}</news:language>
                        </news:publication>
                        <news:publication_date>{self.TEST_DATE_STR_ISO8601}</news:publication_date>
                        <news:title>Foo &lt;foo&gt;</news:title>    <!-- HTML entity decoding -->
                    </news:news>
                </url>
            """

        sitemap_xml += "</urlset>"

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

                Sitemap: {self.TEST_BASE_URL}/sitemap.xml.gz
            """
            ).strip(),
        )

        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap.xml.gz",
            headers={"Content-Type": "application/x-gzip"},
            content=gzip(sitemap_xml),
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        assert len(list(actual_sitemap_tree.all_pages())) == page_count
        assert len(list(actual_sitemap_tree.all_sitemaps())) == 2
