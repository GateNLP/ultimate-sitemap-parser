import textwrap

from tests.tree.base import TreeTestBase
from usp.objects.sitemap import (
    InvalidSitemap,
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
            text=(
                textwrap.dedent(
                    f"""
            User-agent: *
            Disallow: /whatever

            Sitemap: {self.TEST_BASE_URL}/sitemap.xml
        """
                ).strip()
            ),
        )
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap.xml",
            headers={"Content-Type": "application/xml"},
            text=(
                textwrap.dedent(
                    f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                <sitemap>
                    <loc>{self.TEST_BASE_URL}/sitemap.xml</loc>
                    <lastmod>2024-01-01</lastmod>
                </sitemap>
            </sitemapindex>
            """
                ).strip()
            ),
        )

        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)
        sitemaps = list(tree.all_sitemaps())

        assert type(sitemaps[-1]) is InvalidSitemap

    def test_max_recursion_level_sitemap_with_robots(self, requests_mock):
        # GH#29

        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)
        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
            text=(
                textwrap.dedent(
                    f"""
            User-agent: *
            Disallow: /whatever

            Sitemap: {self.TEST_BASE_URL}/sitemap.xml
        """
                ).strip()
            ),
        )
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap.xml",
            headers={"Content-Type": "application/xml"},
            text=(
                textwrap.dedent(
                    f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                <sitemap>
                    <loc>{self.TEST_BASE_URL}/robots.txt</loc>
                    <lastmod>2024-01-01</lastmod>
                </sitemap>
            </sitemapindex>
            """
                ).strip()
            ),
        )

        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)
        sitemaps = list(tree.all_sitemaps())
        assert type(sitemaps[-1]) is InvalidSitemap

    def test_truncated_sitemap_missing_close_urlset(self, requests_mock):
        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
            text=(
                textwrap.dedent(
                    f"""
            User-agent: *
            Disallow: /whatever

            Sitemap: {self.TEST_BASE_URL}/sitemap.xml
        """
                ).strip()
            ),
        )

        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                    xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
                    xmlns:xhtml="http://www.w3.org/1999/xhtml">
        """
        for x in range(50):
            sitemap_xml += f"""
                <url>
                    <loc>{self.TEST_BASE_URL}/page_{x}.html</loc>
                </url>
            """

        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap.xml",
            headers={"Content-Type": "application/xml"},
            text=(textwrap.dedent(sitemap_xml).strip()),
        )

        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)
        assert len(list(tree.all_pages())) == 50

    def test_truncated_sitemap_mid_url(self, requests_mock):
        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
            text=(
                textwrap.dedent(
                    f"""
            User-agent: *
            Disallow: /whatever

            Sitemap: {self.TEST_BASE_URL}/sitemap.xml
        """
                ).strip()
            ),
        )

        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                    xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
                    xmlns:xhtml="http://www.w3.org/1999/xhtml">
        """
        for x in range(49):
            sitemap_xml += f"""
                <url>
                    <loc>{self.TEST_BASE_URL}/page_{x}.html</loc>
                </url>
            """
        sitemap_xml += f"""
            <url>
                <loc>{self.TEST_BASE_URL}/page_
        """

        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap.xml",
            headers={"Content-Type": "application/xml"},
            text=(textwrap.dedent(sitemap_xml).strip()),
        )

        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)
        all_pages = list(tree.all_pages())
        assert len(all_pages) == 49
        assert all_pages[-1].url.endswith("page_48.html")

    def test_301_redirect_to_root(self, requests_mock):
        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
            text=(
                textwrap.dedent(
                    f"""
            User-agent: *
            Disallow: /whatever

            Sitemap: {self.TEST_BASE_URL}/sitemap.xml
            """
                ).strip()
            ),
        )

        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap.xml",
            headers={"Content-Type": "application/xml"},
            text=(
                textwrap.dedent(
                    f"""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                        <sitemap>
                            <loc>{self.TEST_BASE_URL}/sitemap_redir.xml</loc>
                            <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                        </sitemap>
                    </sitemapindex>
                    """
                ).strip()
            ),
        )

        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_redir.xml",
            headers={"Location": self.TEST_BASE_URL + "/sitemap.xml"},
            status_code=301,
        )

        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)
        sub_sitemaps = list(tree.all_sitemaps())
        assert all(type(x) is not InvalidSitemap for x in sub_sitemaps[:-1])
        assert type(sub_sitemaps[-1]) is InvalidSitemap
        assert (
            f"Recursion detected when {self.TEST_BASE_URL}/sitemap_redir.xml redirected to {self.TEST_BASE_URL}/sitemap.xml"
            in str(sub_sitemaps[-1])
        )

    def test_cyclic_sitemap(self, requests_mock):
        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
            text=(
                textwrap.dedent(
                    f"""
            User-agent: *
            Disallow: /whatever

            Sitemap: {self.TEST_BASE_URL}/sitemap_1.xml
            """
                ).strip()
            ),
        )

        for i in range(3):
            requests_mock.get(
                self.TEST_BASE_URL + f"/sitemap_{i + 1}.xml",
                headers={"Content-Type": "application/xml"},
                text=(
                    textwrap.dedent(
                        f"""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                        <sitemap>
                            <loc>{self.TEST_BASE_URL}/sitemap_{i + 2}.xml</loc>
                            <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                        </sitemap>
                    </sitemapindex>
                    """
                    ).strip()
                ),
            )

        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_3.xml",
            headers={"Content-Type": "application/xml"},
            text=(
                textwrap.dedent(
                    f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                    <sitemap>
                        <loc>{self.TEST_BASE_URL}/sitemap_1.xml</loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                    </sitemap>
                </sitemapindex>
                """
                ).strip()
            ),
        )

        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)
        sub_sitemaps = list(tree.all_sitemaps())
        assert all(type(x) is not InvalidSitemap for x in sub_sitemaps[:-1])
        assert type(sub_sitemaps[-1]) is InvalidSitemap
        assert f"Recursion detected in URL {self.TEST_BASE_URL}/sitemap_1.xml" in str(
            sub_sitemaps[-1]
        )

    def test_self_pointing_index(self, requests_mock):
        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)

        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
            text=(
                textwrap.dedent(
                    f"""
            User-agent: *
            Disallow: /whatever

            Sitemap: {self.TEST_BASE_URL}/sitemap.xml
            """
                ).strip()
            ),
        )

        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap.xml",
            headers={"Content-Type": "application/xml"},
            text=(
                textwrap.dedent(
                    f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                    <sitemap>
                        <loc>{self.TEST_BASE_URL}/sitemap.xml</loc>
                        <lastmod>{self.TEST_DATE_STR_ISO8601}</lastmod>
                    </sitemap>
                </sitemapindex>
                """
                ).strip()
            ),
        )

        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)

        sub_sitemaps = list(tree.all_sitemaps())
        assert len(sub_sitemaps) == 3  # robots, sitemap.xml, invalid
        assert all(type(x) is not InvalidSitemap for x in sub_sitemaps[:-1])
        assert type(sub_sitemaps[-1]) is InvalidSitemap
        assert f"Recursion detected in URL {self.TEST_BASE_URL}/sitemap.xml" in str(
            sub_sitemaps[-1]
        )
