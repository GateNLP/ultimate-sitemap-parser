import difflib
import textwrap

from tests.tree.base import TreeTestBase
from usp.objects.page import (
    SitemapNewsStory,
    SitemapPage,
)
from usp.objects.sitemap import (
    IndexRobotsTxtSitemap,
    IndexWebsiteSitemap,
    PagesAtomSitemap,
    PagesRSSSitemap,
)
from usp.tree import sitemap_tree_for_homepage


class TestTreeBasic(TreeTestBase):
    def test_sitemap_tree_for_homepage_rss_atom(self, requests_mock):
        """Test sitemap_tree_for_homepage() with RSS 2.0 / Atom 0.3 / Atom 1.0 feeds."""

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

                Sitemap: {self.TEST_BASE_URL}/sitemap_rss.xml
                Sitemap: {self.TEST_BASE_URL}/sitemap_atom_0_3.xml
                Sitemap: {self.TEST_BASE_URL}/sitemap_atom_1_0.xml
            """
            ).strip(),
        )

        # RSS 2.0 sitemap
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_rss.xml",
            headers={"Content-Type": "application/rss+xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <rss version="2.0">
                    <channel>
                        <title>Test RSS 2.0 feed</title>
                        <description>This is a test RSS 2.0 feed.</description>
                        <link>{self.TEST_BASE_URL}</link>
                        <pubDate>{self.TEST_DATE_STR_RFC2822}</pubDate>

                        <item>
                            <title>Test RSS 2.0 story #1</title>
                            <description>This is a test RSS 2.0 story #1.</description>
                            <link>{self.TEST_BASE_URL}/rss_story_1.html</link>
                            <guid isPermaLink="true">{self.TEST_BASE_URL}/rss_story_1.html</guid>
                            <pubDate>{self.TEST_DATE_STR_RFC2822}</pubDate>
                        </item>

                        <item>
                            <title>Test RSS 2.0 story #2</title>
                            <description>This is a test RSS 2.0 story #2.</description>
                            <link>{self.TEST_BASE_URL}/rss_story_2.html</link>
                            <guid isPermaLink="true">{self.TEST_BASE_URL}/rss_story_2.html</guid>
                            <pubDate>{self.TEST_DATE_STR_RFC2822}</pubDate>
                        </item>

                    </channel>
                </rss>
            """
            ).strip(),
        )

        # Atom 0.3 sitemap
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_atom_0_3.xml",
            headers={"Content-Type": "application/atom+xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <feed version="0.3" xmlns="http://purl.org/atom/ns#">
                    <title>Test Atom 0.3 feed</title>
                    <link rel="alternate" type="text/html" href="{self.TEST_BASE_URL}" />
                    <modified>{self.TEST_DATE_STR_ISO8601}</modified>

                    <entry>
                        <title>Test Atom 0.3 story #1</title>
                        <link rel="alternate" type="text/html" href="{self.TEST_BASE_URL}/atom_0_3_story_1.html" />
                        <id>{self.TEST_BASE_URL}/atom_0_3_story_1.html</id>
                        <issued>{self.TEST_DATE_STR_ISO8601}</issued>
                    </entry>

                    <entry>
                        <title>Test Atom 0.3 story #2</title>
                        <link rel="alternate" type="text/html" href="{self.TEST_BASE_URL}/atom_0_3_story_2.html" />
                        <id>{self.TEST_BASE_URL}/atom_0_3_story_2.html</id>
                        <issued>{self.TEST_DATE_STR_ISO8601}</issued>
                    </entry>

                </feed>
            """
            ).strip(),
        )

        # Atom 1.0 sitemap
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_atom_1_0.xml",
            headers={"Content-Type": "application/atom+xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <feed xmlns="http://www.w3.org/2005/Atom">
                    <title>Test Atom 1.0 feed</title>
                    <subtitle>This is a test Atom 1.0 feed.</subtitle>
                    <link href="{self.TEST_BASE_URL}/sitemap_atom_1_0.xml" rel="self" />
                    <link href="{self.TEST_BASE_URL}" />
                    <id>{self.TEST_BASE_URL}</id>
                    <updated>{self.TEST_DATE_STR_ISO8601}</updated>

                    <entry>
                        <title>Test Atom 1.0 story #1</title>
                        <link href="{self.TEST_BASE_URL}/atom_1_0_story_1.html" />
                        <link rel="alternate" type="text/html" href="{self.TEST_BASE_URL}/atom_1_0_story_1.html?alt" />
                        <link rel="edit" href="{self.TEST_BASE_URL}/atom_1_0_story_1.html?edit" />
                        <id>{self.TEST_BASE_URL}/atom_1_0_story_1.html</id>
                        <updated>{self.TEST_DATE_STR_ISO8601}</updated>
                        <summary>This is test atom 1.0 story #1.</summary>
                        <content type="xhtml">
                            <div xmlns="http://www.w3.org/1999/xhtml">
                                <p>This is test atom 1.0 story #1.</p>
                            </div>
                        </content>
                        <author>
                            <name>John Doe</name>
                            <email>johndoe@example.com</email>
                        </author>
                    </entry>

                    <entry>
                        <title>Test Atom 1.0 story #2</title>
                        <link href="{self.TEST_BASE_URL}/atom_1_0_story_2.html" />
                        <link rel="alternate" type="text/html" href="{self.TEST_BASE_URL}/atom_1_0_story_2.html?alt" />
                        <link rel="edit" href="{self.TEST_BASE_URL}/atom_1_0_story_2.html?edit" />
                        <id>{self.TEST_BASE_URL}/atom_1_0_story_2.html</id>
                        <updated>{self.TEST_DATE_STR_ISO8601}</updated>
                        <summary>This is test atom 1.0 story #2.</summary>
                        <content type="xhtml">
                            <div xmlns="http://www.w3.org/1999/xhtml">
                                <p>This is test atom 1.0 story #2.</p>
                            </div>
                        </content>
                        <author>
                            <name>John Doe</name>
                            <email>johndoe@example.com</email>
                        </author>
                    </entry>

                </feed>
            """
            ).strip(),
        )

        expected_sitemap_tree = IndexWebsiteSitemap(
            url=f"{self.TEST_BASE_URL}/",
            sub_sitemaps=[
                IndexRobotsTxtSitemap(
                    url=f"{self.TEST_BASE_URL}/robots.txt",
                    sub_sitemaps=[
                        PagesRSSSitemap(
                            url=f"{self.TEST_BASE_URL}/sitemap_rss.xml",
                            pages=[
                                SitemapPage(
                                    url=f"{self.TEST_BASE_URL}/rss_story_1.html",
                                    news_story=SitemapNewsStory(
                                        title="Test RSS 2.0 story #1",
                                        publish_date=self.TEST_DATE_DATETIME,
                                    ),
                                ),
                                SitemapPage(
                                    url=f"{self.TEST_BASE_URL}/rss_story_2.html",
                                    news_story=SitemapNewsStory(
                                        title="Test RSS 2.0 story #2",
                                        publish_date=self.TEST_DATE_DATETIME,
                                    ),
                                ),
                            ],
                        ),
                        PagesAtomSitemap(
                            url=f"{self.TEST_BASE_URL}/sitemap_atom_0_3.xml",
                            pages=[
                                SitemapPage(
                                    url=f"{self.TEST_BASE_URL}/atom_0_3_story_1.html",
                                    news_story=SitemapNewsStory(
                                        title="Test Atom 0.3 story #1",
                                        publish_date=self.TEST_DATE_DATETIME,
                                    ),
                                ),
                                SitemapPage(
                                    url=f"{self.TEST_BASE_URL}/atom_0_3_story_2.html",
                                    news_story=SitemapNewsStory(
                                        title="Test Atom 0.3 story #2",
                                        publish_date=self.TEST_DATE_DATETIME,
                                    ),
                                ),
                            ],
                        ),
                        PagesAtomSitemap(
                            url=f"{self.TEST_BASE_URL}/sitemap_atom_1_0.xml",
                            pages=[
                                SitemapPage(
                                    url=f"{self.TEST_BASE_URL}/atom_1_0_story_1.html",
                                    news_story=SitemapNewsStory(
                                        title="Test Atom 1.0 story #1",
                                        publish_date=self.TEST_DATE_DATETIME,
                                    ),
                                ),
                                SitemapPage(
                                    url=f"{self.TEST_BASE_URL}/atom_1_0_story_2.html",
                                    news_story=SitemapNewsStory(
                                        title="Test Atom 1.0 story #2",
                                        publish_date=self.TEST_DATE_DATETIME,
                                    ),
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
        diff = difflib.ndiff(expected_lines, actual_lines)
        diff_str = "\n".join(diff)

        assert expected_sitemap_tree == actual_sitemap_tree, diff_str

        assert len(list(actual_sitemap_tree.all_pages())) == 6
        assert len(list(actual_sitemap_tree.all_sitemaps())) == 4

    def test_sitemap_tree_for_homepage_rss_atom_empty(self, requests_mock):
        """Test sitemap_tree_for_homepage() with empty RSS 2.0 / Atom 0.3 / Atom 1.0 feeds."""

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

                Sitemap: {self.TEST_BASE_URL}/sitemap_rss.xml
                Sitemap: {self.TEST_BASE_URL}/sitemap_atom_0_3.xml
                Sitemap: {self.TEST_BASE_URL}/sitemap_atom_1_0.xml
            """
            ).strip(),
        )

        # RSS 2.0 sitemap
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_rss.xml",
            headers={"Content-Type": "application/rss+xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <rss version="2.0">
                    <channel>
                        <title>Test RSS 2.0 feed</title>
                        <description>This is a test RSS 2.0 feed.</description>
                        <link>{self.TEST_BASE_URL}</link>
                        <pubDate>{self.TEST_DATE_STR_RFC2822}</pubDate>
                    </channel>
                </rss>
            """
            ).strip(),
        )

        # Atom 0.3 sitemap
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_atom_0_3.xml",
            headers={"Content-Type": "application/atom+xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <feed version="0.3" xmlns="http://purl.org/atom/ns#">
                    <title>Test Atom 0.3 feed</title>
                    <link rel="alternate" type="text/html" href="{self.TEST_BASE_URL}" />
                    <modified>{self.TEST_DATE_STR_ISO8601}</modified>
                </feed>
            """
            ).strip(),
        )

        # Atom 1.0 sitemap
        requests_mock.get(
            self.TEST_BASE_URL + "/sitemap_atom_1_0.xml",
            headers={"Content-Type": "application/atom+xml"},
            text=textwrap.dedent(
                f"""
                <?xml version="1.0" encoding="UTF-8"?>
                <feed xmlns="http://www.w3.org/2005/Atom">
                    <title>Test Atom 1.0 feed</title>
                    <subtitle>This is a test Atom 1.0 feed.</subtitle>
                    <link href="{self.TEST_BASE_URL}/sitemap_atom_1_0.xml" rel="self" />
                    <link href="{self.TEST_BASE_URL}" />
                    <id>{self.TEST_BASE_URL}</id>
                    <updated>{self.TEST_DATE_STR_ISO8601}</updated>
                </feed>
            """
            ).strip(),
        )

        expected_sitemap_tree = IndexWebsiteSitemap(
            url=f"{self.TEST_BASE_URL}/",
            sub_sitemaps=[
                IndexRobotsTxtSitemap(
                    url=f"{self.TEST_BASE_URL}/robots.txt",
                    sub_sitemaps=[
                        PagesRSSSitemap(
                            url=f"{self.TEST_BASE_URL}/sitemap_rss.xml",
                            pages=[],
                        ),
                        PagesAtomSitemap(
                            url=f"{self.TEST_BASE_URL}/sitemap_atom_0_3.xml",
                            pages=[],
                        ),
                        PagesAtomSitemap(
                            url=f"{self.TEST_BASE_URL}/sitemap_atom_1_0.xml",
                            pages=[],
                        ),
                    ],
                )
            ],
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        assert expected_sitemap_tree == actual_sitemap_tree

        assert len(list(actual_sitemap_tree.all_pages())) == 0
        assert len(list(actual_sitemap_tree.all_sitemaps())) == 4
