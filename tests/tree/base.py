import datetime
from email.utils import format_datetime
import textwrap

from dateutil.tz import tzoffset
import requests_mock as rq_mock


class TreeTestBase:
    TEST_BASE_URL = "http://test_ultimate-sitemap-parser.com"  # mocked by HTTPretty

    # Publication / "last modified" date
    TEST_DATE_DATETIME = datetime.datetime(
        year=2009,
        month=12,
        day=17,
        hour=12,
        minute=4,
        second=56,
        tzinfo=tzoffset(None, 7200),
    )
    TEST_DATE_STR_RFC2822 = format_datetime(TEST_DATE_DATETIME)
    """Test string date formatted as RFC 2822 (for RSS 2.0 sitemaps)."""
    TEST_DATE_STR_ISO8601 = TEST_DATE_DATETIME.isoformat()
    """Test string date formatted as ISO 8601 (for XML and Atom 0.3 / 1.0 sitemaps)."""

    TEST_PUBLICATION_LANGUAGE = "en"
    TEST_PUBLICATION_NAME = "Test publication"

    @staticmethod
    def fallback_to_404_not_found_matcher(request):
        """Reply with "404 Not Found" to unmatched URLs instead of throwing NoMockAddress."""
        return rq_mock.create_response(
            request,
            status_code=404,
            reason="Not Found",
            headers={"Content-Type": "text/html"},
            text="<h1>404 Not Found!</h1>",
        )

    def init_basic_sitemap(self, requests_mock):
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

                Sitemap: {self.TEST_BASE_URL}/sitemap_pages.xml

                # Intentionally spelled as "Site-map" as Google tolerates this:
                # https://github.com/google/robotstxt/blob/master/robots.cc#L703 
                Site-map: {self.TEST_BASE_URL}/sitemap_news_index_1.xml
            """
            ).strip(),
        )

        # One sitemap for random static pages
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_pages.xml",
            headers={"Content-Type": "application/xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                    <url>
                        <loc>{self.TEST_BASE_URL}/about.html</loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                        <changefreq>monthly</changefreq>
                        <priority>0.8</priority>
                    </url>
                    <url>
                        <loc>{self.TEST_BASE_URL}/contact.html</loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>

                        <!-- Invalid change frequency -->
                        <changefreq>when we feel like it</changefreq>

                        <!-- Invalid priority -->
                        <priority>1.1</priority>

                    </url>
                </urlset>
            """
            ).strip(),
        )

        # Index sitemap pointing to sitemaps with stories
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_news_index_1.xml",
            headers={"Content-Type": "application/xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                    <sitemap>
                        <loc>{self.TEST_BASE_URL}/sitemap_news_1.xml</loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                    </sitemap>
                    <sitemap>
                        <loc>{self.TEST_BASE_URL}/sitemap_news_index_2.xml</loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                    </sitemap>
                </sitemapindex>
            """
            ).strip(),
        )

        # First sitemap with actual stories
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_news_1.xml",
            headers={"Content-Type": "application/xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
                        xmlns:xhtml="http://www.w3.org/1999/xhtml">

                    <url>
                        <loc>{self.TEST_BASE_URL}/news/foo.html</loc>

                        <!-- Element present but empty -->
                        <lastmod />

                        <!-- Some other XML namespace -->
                        <xhtml:link rel="alternate"
                                    media="only screen and (max-width: 640px)"
                                    href="{self.TEST_BASE_URL}/news/foo.html?mobile=1" />

                        <news:news>
                            <news:publication>
                                <news:name>{self.TEST_PUBLICATION_NAME}</news:name>
                                <news:language>{self.TEST_PUBLICATION_LANGUAGE}</news:language>
                            </news:publication>
                            <news:publication_date>{self.TEST_DATE_STR_ISO8601}</news:publication_date>
                            <news:title>Foo &lt;foo&gt;</news:title>    <!-- HTML entity decoding -->
                        </news:news>
                    </url>

                    <!-- Has a duplicate story in /sitemap_news_2.xml -->
                    <url>
                        <loc>{self.TEST_BASE_URL}/news/bar.html</loc>
                        <xhtml:link rel="alternate"
                                    media="only screen and (max-width: 640px)"
                                    href="{self.TEST_BASE_URL}/news/bar.html?mobile=1" />
                        <news:news>
                            <news:publication>
                                <news:name>{self.TEST_PUBLICATION_NAME}</news:name>
                                <news:language>{self.TEST_PUBLICATION_LANGUAGE}</news:language>
                            </news:publication>
                            <news:publication_date>{self.TEST_DATE_STR_ISO8601}</news:publication_date>
                            <news:title>Bar &amp; bar</news:title>
                        </news:news>
                    </url>

                </urlset>
            """
            ).strip(),
        )

        # Another index sitemap pointing to a second sitemaps with stories
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_news_index_2.xml",
            headers={"Content-Type": "application/xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

                    <sitemap>
                        <!-- Extra whitespace added around URL -->
                        <loc>  {self.TEST_BASE_URL}/sitemap_news_2.xml  </loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                    </sitemap>

                    <!-- Nonexistent sitemap -->
                    <sitemap>
                        <loc>{self.TEST_BASE_URL}/sitemap_news_missing.xml</loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                    </sitemap>

                </sitemapindex>
            """
            ).strip(),
        )

        # Second sitemap with actual stories
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_news_2.xml",
            headers={"Content-Type": "application/xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                        xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
                        xmlns:xhtml="http://www.w3.org/1999/xhtml">

                    <!-- Has a duplicate story in /sitemap_news_1.xml -->
                    <url>
                        <!-- Extra whitespace added around URL -->
                        <loc>  {self.TEST_BASE_URL}/news/bar.html  </loc>
                        <xhtml:link rel="alternate"
                                    media="only screen and (max-width: 640px)"
                                    href="{self.TEST_BASE_URL}/news/bar.html?mobile=1#fragment_is_to_be_removed" />
                        <news:news>
                            <news:publication>
                                <news:name>{self.TEST_PUBLICATION_NAME}</news:name>
                                <news:language>{self.TEST_PUBLICATION_LANGUAGE}</news:language>
                            </news:publication>
                            <news:publication_date>{self.TEST_DATE_STR_ISO8601}</news:publication_date>

                            <tag_without_inner_character_data name="value" />

                            <news:title>Bar &amp; bar</news:title>
                        </news:news>
                    </url>

                    <url>
                        <loc>{self.TEST_BASE_URL}/news/baz.html</loc>
                        <xhtml:link rel="alternate"
                                    media="only screen and (max-width: 640px)"
                                    href="{self.TEST_BASE_URL}/news/baz.html?mobile=1" />
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

        # Nonexistent sitemap
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_news_missing.xml",
            status_code=404,
            reason="Not Found",
            headers={"Content-Type": "text/html"},
            text="<h1>404 Not Found!</h1>",
        )
