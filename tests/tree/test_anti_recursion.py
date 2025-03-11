import textwrap

from tests.tree.base import TreeTestBase
from usp.objects.sitemap import IndexRobotsTxtSitemap, InvalidSitemap
from usp.tree import sitemap_tree_for_homepage


class TestTreeAntiRecursion(TreeTestBase):
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

    def test_known_path_redirects(self, requests_mock):
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
                        </urlset>
                    """
            ).strip(),
        )

        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap-index.xml",
            headers={"Location": self.TEST_BASE_URL + "/sitemap.xml"},
            status_code=301,
        )

        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)
        # homepage should only have robots child, not sitemap discovered through known URL
        assert len(tree.sub_sitemaps) == 1
        assert type(tree.sub_sitemaps[0]) is IndexRobotsTxtSitemap
