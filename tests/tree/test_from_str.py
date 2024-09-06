import textwrap

from tests.tree.base import TreeTestBase
from usp.objects.page import SitemapPage
from usp.objects.sitemap import IndexXMLSitemap, InvalidSitemap, PagesXMLSitemap
from usp.tree import sitemap_from_str


class TestSitemapFromStrStr(TreeTestBase):
    def test_xml_pages(self):
        parsed = sitemap_from_str(
            content=textwrap.dedent(
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
            ).strip()
        )

        assert isinstance(parsed, PagesXMLSitemap)
        assert len(list(parsed.all_pages())) == 2
        assert all([isinstance(page, SitemapPage) for page in parsed.all_pages()])

    def test_xml_index(self):
        parsed = sitemap_from_str(
            content=textwrap.dedent(
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
            ).strip()
        )

        assert isinstance(parsed, IndexXMLSitemap)
        assert len(parsed.sub_sitemaps) == 2
        assert all(
            [
                isinstance(sub_sitemap, InvalidSitemap)
                for sub_sitemap in parsed.sub_sitemaps
            ]
        )
        assert parsed.sub_sitemaps[0].url == self.TEST_BASE_URL + "/sitemap_news_1.xml"
