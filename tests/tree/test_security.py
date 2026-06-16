import textwrap

from tests.tree.base import TreeTestBase
from usp.objects.sitemap import (
    InvalidSitemap,
)
from usp.tree import sitemap_tree_for_homepage


class TestTreeSecurity(TreeTestBase):
    def test_billion_laughs_attack(self, requests_mock, caplog):
        requests_mock.add_matcher(TreeTestBase.fallback_to_404_not_found_matcher)
        requests_mock.get(
            self.TEST_BASE_URL + "/robots.txt",
            headers={"Content-Type": "text/plain"},
            text=textwrap.dedent(
                f"""
                Sitemap: {self.TEST_BASE_URL}/sitemap.xml
                """
            ).strip(),
        )

        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap.xml",
            headers={"Content-Type": "application/xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE lolz [
                <!ENTITY lol "lol">
                <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol
;&lol;&lol;&lol;">
                <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
                <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
                <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
                <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
                <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
                <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
                <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
                 <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
                ]>
                <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                    <url>
                        <loc>{self.TEST_BASE_URL}/page.html</loc>
                    </url>
                </urlset>
                """
            ).strip(),
        )

        tree = sitemap_tree_for_homepage(self.TEST_BASE_URL)
        sitemaps = list(tree.all_sitemaps())
        assert type(sitemaps[-1]) is InvalidSitemap

        assert (
            "Sitemap contained unexpected non-standard XML DOCTYPE. Parsing not supported for security reasons."
            in caplog.text
        )
