import textwrap

from tests.tree.base import TreeTestBase
from usp.objects.page import SitemapImage, SitemapPage
from usp.objects.sitemap import (
    IndexRobotsTxtSitemap,
    IndexWebsiteSitemap,
    PagesXMLSitemap,
)
from usp.tree import sitemap_tree_for_homepage


class TestXMLExts(TreeTestBase):
    def test_xml_image(self, requests_mock):
        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
            text=textwrap.dedent(
                f"""
                User-agent: *
                Disallow: /whatever

                Sitemap: {self.TEST_BASE_URL}/sitemap_images.xml

            """
            ).strip(),
        )

        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_images.xml",
            headers={"Content-Type": "text/xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                    xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
                  <url>
                    <loc>{self.TEST_BASE_URL}/sample1.html</loc>
                    <image:image>
                      <image:loc>{self.TEST_BASE_URL}/image.jpg</image:loc>
                      <image:caption>Example Caption</image:caption>
                      <image:geo_location>Sheffield, UK</image:geo_location>
                      <image:title>Example Title</image:title>
                      <image:license>https://creativecommons.org/publicdomain/zero/1.0/</image:license>
                    </image:image>
                    <image:image>
                      <image:loc>{self.TEST_BASE_URL}/photo.jpg</image:loc>
                    </image:image>
                  </url>
                  <url>
                    <loc>{self.TEST_BASE_URL}/sample2.html</loc>
                    <image:image>
                      <image:loc>{self.TEST_BASE_URL}/picture.jpg</image:loc>
                    </image:image>
                  </url>
                </urlset>
                """
            ).strip(),
        )

        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)

        expected_sitemap_tree = IndexWebsiteSitemap(
            url=f"{self.TEST_BASE_URL}/",
            sub_sitemaps=[
                IndexRobotsTxtSitemap(
                    url=f"{self.TEST_BASE_URL}/robots.txt",
                    sub_sitemaps=[
                        PagesXMLSitemap(
                            url=f"{self.TEST_BASE_URL}/sitemap_images.xml",
                            pages=[
                                SitemapPage(
                                    url=f"{self.TEST_BASE_URL}/sample1.html",
                                    images=[
                                        SitemapImage(
                                            loc=f"{self.TEST_BASE_URL}/image.jpg",
                                            caption="Example Caption",
                                            geo_location="Sheffield, UK",
                                            title="Example Title",
                                            license_="https://creativecommons.org/publicdomain/zero/1.0/",
                                        ),
                                        SitemapImage(
                                            loc=f"{self.TEST_BASE_URL}/photo.jpg"
                                        ),
                                    ],
                                ),
                                SitemapPage(
                                    url=f"{self.TEST_BASE_URL}/sample2.html",
                                    images=[
                                        SitemapImage(
                                            loc=f"{self.TEST_BASE_URL}/picture.jpg"
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                )
            ],
        )

        print(tree.to_dict())
        print(tree)

        assert tree == expected_sitemap_tree


class TestXMLHrefLang(TreeTestBase):
    def test_hreflang(self, requests_mock):
        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

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
            headers={"Content-Type": "text/xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
                    <url>
                        <loc>{self.TEST_BASE_URL}/en/page</loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                        <changefreq>monthly</changefreq>
                        <priority>0.8</priority>
                        <xhtml:link rel="alternate" hreflang="fr-FR" href="{self.TEST_BASE_URL}/fr/page"/>
                    </url>
                    <url>
                        <loc>{self.TEST_BASE_URL}/fr/page</loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                        <changefreq>monthly</changefreq>
                        <priority>0.8</priority>
                        <xhtml:link rel="alternate" hreflang="en-GB" href="{self.TEST_BASE_URL}/en/page"/>
                    </url>
                </urlset>
                """
            ).strip(),
        )

        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)

        pages = list(tree.all_pages())
        assert pages[0].alternates == [
            ("fr-FR", f"{self.TEST_BASE_URL}/fr/page"),
        ]
        assert pages[1].alternates == [
            ("en-GB", f"{self.TEST_BASE_URL}/en/page"),
        ]

    def test_missing_attrs(self, requests_mock):
        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

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
            headers={"Content-Type": "text/xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
                    <url>
                        <loc>{self.TEST_BASE_URL}/en/page</loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                        <changefreq>monthly</changefreq>
                        <priority>0.8</priority>
                        <xhtml:link rel="alternate" href="{self.TEST_BASE_URL}/fr/page"/>
                    </url>
                    <url>
                        <loc>{self.TEST_BASE_URL}/en/page2</loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                        <changefreq>monthly</changefreq>
                        <priority>0.8</priority>
                        <xhtml:link hreflang="fr-FR" href="{self.TEST_BASE_URL}/fr/page2"/>
                    </url>
                    <url>
                        <loc>{self.TEST_BASE_URL}/fr/page</loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                        <changefreq>monthly</changefreq>
                        <priority>0.8</priority>
                        <xhtml:link rel="alternate" hreflang="en-GB"/>
                    </url>
                    <url>
                        <loc>{self.TEST_BASE_URL}/fr/page2</loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                        <changefreq>monthly</changefreq>
                        <priority>0.8</priority>
                        <xhtml:link hreflang="en-GB" href="{self.TEST_BASE_URL}/en/page2"/>
                    </url>
                </urlset>
                """
            ).strip(),
        )

        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)

        pages = list(tree.all_pages())
        assert pages[0].alternates is None
        assert pages[1].alternates is None
        assert pages[2].alternates is None
        assert pages[3].alternates is None
