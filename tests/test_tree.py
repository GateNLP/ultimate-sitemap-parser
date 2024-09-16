import datetime
import difflib
import textwrap
from decimal import Decimal
from email.utils import format_datetime
from unittest import TestCase

import requests_mock
from dateutil.tz import tzoffset

from tests.helpers import gzip
from usp.log import create_logger
from usp.objects.page import (
    SitemapPage,
    SitemapNewsStory,
    SitemapPageChangeFrequency,
)
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
from usp.tree import sitemap_tree_for_homepage

# FIXME various exotic properties
# FIXME XML vulnerabilities with Expat
# FIXME max. recursion level
# FIXME tests responses that are too big


log = create_logger(__name__)


class TestSitemapTree(TestCase):
    TEST_BASE_URL = 'http://test_ultimate-sitemap-parser.com'  # mocked by HTTPretty

    # Publication / "last modified" date
    TEST_DATE_DATETIME = datetime.datetime(
        year=2009, month=12, day=17, hour=12, minute=4, second=56,
        tzinfo=tzoffset(None, 7200),
    )
    TEST_DATE_STR_ISO8601 = TEST_DATE_DATETIME.isoformat()
    """Test string date formatted as ISO 8601 (for XML and Atom 0.3 / 1.0 sitemaps)."""

    TEST_DATE_STR_RFC2822 = format_datetime(TEST_DATE_DATETIME)
    """Test string date formatted as RFC 2822 (for RSS 2.0 sitemaps)."""

    TEST_PUBLICATION_NAME = 'Test publication'
    TEST_PUBLICATION_LANGUAGE = 'en'

    @staticmethod
    def fallback_to_404_not_found_matcher(request):
        """Reply with "404 Not Found" to unmatched URLs instead of throwing NoMockAddress."""
        return requests_mock.create_response(
            request,
            status_code=404,
            reason='Not Found',
            headers={'Content-Type': 'text/html'},
            text="<h1>404 Not Found!</h1>",
        )

    # noinspection DuplicatedCode
    def test_sitemap_tree_for_homepage(self):
        """Test sitemap_tree_for_homepage()."""

        with requests_mock.Mocker() as m:
            m.add_matcher(TestSitemapTree.fallback_to_404_not_found_matcher)

            m.get(
                self.TEST_BASE_URL + '/',
                text='This is a homepage.',
            )

            m.get(
                self.TEST_BASE_URL + '/robots.txt',
                headers={'Content-Type': 'text/plain'},
                text=textwrap.dedent("""
                    User-agent: *
                    Disallow: /whatever
    
                    Sitemap: {base_url}/sitemap_pages.xml
                    
                    # Intentionally spelled as "Site-map" as Google tolerates this:
                    # https://github.com/google/robotstxt/blob/master/robots.cc#L703 
                    Site-map: {base_url}/sitemap_news_index_1.xml
                """.format(base_url=self.TEST_BASE_URL)).strip(),
            )

            # One sitemap for random static pages
            m.get(
                self.TEST_BASE_URL + '/sitemap_pages.xml',
                headers={'Content-Type': 'application/xml'},
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                        <url>
                            <loc>{base_url}/about.html</loc>
                            <lastmod>{last_modified_date}</lastmod>
                            <changefreq>monthly</changefreq>
                            <priority>0.8</priority>
                        </url>
                        <url>
                            <loc>{base_url}/contact.html</loc>
                            <lastmod>{last_modified_date}</lastmod>
    
                            <!-- Invalid change frequency -->
                            <changefreq>when we feel like it</changefreq>
    
                            <!-- Invalid priority -->
                            <priority>1.1</priority>
    
                        </url>
                    </urlset>
                """.format(base_url=self.TEST_BASE_URL, last_modified_date=self.TEST_DATE_STR_ISO8601)).strip(),
            )

            # Index sitemap pointing to sitemaps with stories
            m.get(
                self.TEST_BASE_URL + '/sitemap_news_index_1.xml',
                headers={'Content-Type': 'application/xml'},
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                        <sitemap>
                            <loc>{base_url}/sitemap_news_1.xml</loc>
                            <lastmod>{last_modified}</lastmod>
                        </sitemap>
                        <sitemap>
                            <loc>{base_url}/sitemap_news_index_2.xml</loc>
                            <lastmod>{last_modified}</lastmod>
                        </sitemap>
                    </sitemapindex>
                """.format(base_url=self.TEST_BASE_URL, last_modified=self.TEST_DATE_STR_ISO8601)).strip(),
            )

            # First sitemap with actual stories
            m.get(
                self.TEST_BASE_URL + '/sitemap_news_1.xml',
                headers={'Content-Type': 'application/xml'},
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                            xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
                            xmlns:xhtml="http://www.w3.org/1999/xhtml">
    
                        <url>
                            <loc>{base_url}/news/foo.html</loc>
    
                            <!-- Element present but empty -->
                            <lastmod />
    
                            <!-- Some other XML namespace -->
                            <xhtml:link rel="alternate"
                                        media="only screen and (max-width: 640px)"
                                        href="{base_url}/news/foo.html?mobile=1" />
    
                            <news:news>
                                <news:publication>
                                    <news:name>{publication_name}</news:name>
                                    <news:language>{publication_language}</news:language>
                                </news:publication>
                                <news:publication_date>{publication_date}</news:publication_date>
                                <news:title>Foo &lt;foo&gt;</news:title>    <!-- HTML entity decoding -->
                            </news:news>
                        </url>
    
                        <!-- Has a duplicate story in /sitemap_news_2.xml -->
                        <url>
                            <loc>{base_url}/news/bar.html</loc>
                            <xhtml:link rel="alternate"
                                        media="only screen and (max-width: 640px)"
                                        href="{base_url}/news/bar.html?mobile=1" />
                            <news:news>
                                <news:publication>
                                    <news:name>{publication_name}</news:name>
                                    <news:language>{publication_language}</news:language>
                                </news:publication>
                                <news:publication_date>{publication_date}</news:publication_date>
                                <news:title>Bar &amp; bar</news:title>
                            </news:news>
                        </url>
    
                    </urlset>
                """.format(
                    base_url=self.TEST_BASE_URL,
                    publication_name=self.TEST_PUBLICATION_NAME,
                    publication_language=self.TEST_PUBLICATION_LANGUAGE,
                    publication_date=self.TEST_DATE_STR_ISO8601,
                )).strip(),
            )

            # Another index sitemap pointing to a second sitemaps with stories
            m.get(
                self.TEST_BASE_URL + '/sitemap_news_index_2.xml',
                headers={'Content-Type': 'application/xml'},
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    
                        <sitemap>
                            <!-- Extra whitespace added around URL -->
                            <loc>  {base_url}/sitemap_news_2.xml  </loc>
                            <lastmod>{last_modified}</lastmod>
                        </sitemap>
    
                        <!-- Nonexistent sitemap -->
                        <sitemap>
                            <loc>{base_url}/sitemap_news_missing.xml</loc>
                            <lastmod>{last_modified}</lastmod>
                        </sitemap>
    
                    </sitemapindex>
                """.format(base_url=self.TEST_BASE_URL, last_modified=self.TEST_DATE_STR_ISO8601)).strip(),
            )

            # Second sitemap with actual stories
            m.get(
                self.TEST_BASE_URL + '/sitemap_news_2.xml',
                headers={'Content-Type': 'application/xml'},
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                            xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
                            xmlns:xhtml="http://www.w3.org/1999/xhtml">
    
                        <!-- Has a duplicate story in /sitemap_news_1.xml -->
                        <url>
                            <!-- Extra whitespace added around URL -->
                            <loc>  {base_url}/news/bar.html  </loc>
                            <xhtml:link rel="alternate"
                                        media="only screen and (max-width: 640px)"
                                        href="{base_url}/news/bar.html?mobile=1#fragment_is_to_be_removed" />
                            <news:news>
                                <news:publication>
                                    <news:name>{publication_name}</news:name>
                                    <news:language>{publication_language}</news:language>
                                </news:publication>
                                <news:publication_date>{publication_date}</news:publication_date>
    
                                <tag_without_inner_character_data name="value" />
    
                                <news:title>Bar &amp; bar</news:title>
                            </news:news>
                        </url>
    
                        <url>
                            <loc>{base_url}/news/baz.html</loc>
                            <xhtml:link rel="alternate"
                                        media="only screen and (max-width: 640px)"
                                        href="{base_url}/news/baz.html?mobile=1" />
                            <news:news>
                                <news:publication>
                                    <news:name>{publication_name}</news:name>
                                    <news:language>{publication_language}</news:language>
                                </news:publication>
                                <news:publication_date>{publication_date}</news:publication_date>
                                <news:title><![CDATA[Bąž]]></news:title>    <!-- CDATA and UTF-8 -->
                            </news:news>
                        </url>
    
                    </urlset>
                """.format(
                    base_url=self.TEST_BASE_URL,
                    publication_name=self.TEST_PUBLICATION_NAME,
                    publication_language=self.TEST_PUBLICATION_LANGUAGE,
                    publication_date=self.TEST_DATE_STR_ISO8601,
                )).strip(),
            )

            # Nonexistent sitemap
            m.get(
                self.TEST_BASE_URL + '/sitemap_news_missing.xml',
                status_code=404,
                reason='Not Found',
                headers={'Content-Type': 'text/html'},
                text="<h1>404 Not Found!</h1>",
            )

            expected_sitemap_tree = IndexWebsiteSitemap(
                url='{}/'.format(self.TEST_BASE_URL),
                sub_sitemaps=[
                    IndexRobotsTxtSitemap(
                        url='{}/robots.txt'.format(self.TEST_BASE_URL),
                        sub_sitemaps=[
                            PagesXMLSitemap(
                                url='{}/sitemap_pages.xml'.format(self.TEST_BASE_URL),
                                pages=[
                                    SitemapPage(
                                        url='{}/about.html'.format(self.TEST_BASE_URL),
                                        last_modified=self.TEST_DATE_DATETIME,
                                        news_story=None,
                                        change_frequency=SitemapPageChangeFrequency.MONTHLY,
                                        priority=Decimal('0.8'),
                                    ),
                                    SitemapPage(
                                        url='{}/contact.html'.format(self.TEST_BASE_URL),
                                        last_modified=self.TEST_DATE_DATETIME,
                                        news_story=None,

                                        # Invalid input -- should be reset to "always"
                                        change_frequency=SitemapPageChangeFrequency.ALWAYS,

                                        # Invalid input -- should be reset to 0.5 (the default as per the spec)
                                        priority=Decimal('0.5'),

                                    )
                                ],
                            ),
                            IndexXMLSitemap(
                                url='{}/sitemap_news_index_1.xml'.format(self.TEST_BASE_URL),
                                sub_sitemaps=[
                                    PagesXMLSitemap(
                                        url='{}/sitemap_news_1.xml'.format(self.TEST_BASE_URL),
                                        pages=[
                                            SitemapPage(
                                                url='{}/news/foo.html'.format(self.TEST_BASE_URL),
                                                news_story=SitemapNewsStory(
                                                    title='Foo <foo>',
                                                    publish_date=self.TEST_DATE_DATETIME,
                                                    publication_name=self.TEST_PUBLICATION_NAME,
                                                    publication_language=self.TEST_PUBLICATION_LANGUAGE,
                                                ),
                                            ),
                                            SitemapPage(
                                                url='{}/news/bar.html'.format(self.TEST_BASE_URL),
                                                news_story=SitemapNewsStory(
                                                    title='Bar & bar',
                                                    publish_date=self.TEST_DATE_DATETIME,
                                                    publication_name=self.TEST_PUBLICATION_NAME,
                                                    publication_language=self.TEST_PUBLICATION_LANGUAGE,
                                                ),
                                            ),
                                        ]
                                    ),
                                    IndexXMLSitemap(
                                        url='{}/sitemap_news_index_2.xml'.format(self.TEST_BASE_URL),
                                        sub_sitemaps=[
                                            PagesXMLSitemap(
                                                url='{}/sitemap_news_2.xml'.format(self.TEST_BASE_URL),
                                                pages=[
                                                    SitemapPage(
                                                        url='{}/news/bar.html'.format(self.TEST_BASE_URL),
                                                        news_story=SitemapNewsStory(
                                                            title='Bar & bar',
                                                            publish_date=self.TEST_DATE_DATETIME,
                                                            publication_name=self.TEST_PUBLICATION_NAME,
                                                            publication_language=self.TEST_PUBLICATION_LANGUAGE,
                                                        ),
                                                    ),
                                                    SitemapPage(
                                                        url='{}/news/baz.html'.format(self.TEST_BASE_URL),
                                                        news_story=SitemapNewsStory(
                                                            title='Bąž',
                                                            publish_date=self.TEST_DATE_DATETIME,
                                                            publication_name=self.TEST_PUBLICATION_NAME,
                                                            publication_language=self.TEST_PUBLICATION_LANGUAGE,
                                                        ),
                                                    ),
                                                ],
                                            ),
                                            InvalidSitemap(
                                                url='{}/sitemap_news_missing.xml'.format(self.TEST_BASE_URL),
                                                reason=(
                                                    'Unable to fetch sitemap from {base_url}/sitemap_news_missing.xml: '
                                                    '404 Not Found'
                                                ).format(base_url=self.TEST_BASE_URL),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    )
                ]
            )

            actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

            expected_lines = str(expected_sitemap_tree).split()
            actual_lines = str(actual_sitemap_tree).split()
            diff = difflib.ndiff(expected_lines, actual_lines)
            diff_str = '\n'.join(diff)

            assert expected_sitemap_tree == actual_sitemap_tree, diff_str

            assert len(list(actual_sitemap_tree.all_pages())) == 6

    def test_sitemap_tree_for_homepage_gzip(self):
        """Test sitemap_tree_for_homepage() with gzipped sitemaps."""

        with requests_mock.Mocker() as m:
            m.add_matcher(TestSitemapTree.fallback_to_404_not_found_matcher)

            m.get(
                self.TEST_BASE_URL + '/',
                text='This is a homepage.',
            )

            m.get(
                self.TEST_BASE_URL + '/robots.txt',
                headers={'Content-Type': 'text/plain'},
                text=textwrap.dedent("""
                    User-agent: *
                    Disallow: /whatever
    
                    Sitemap: {base_url}/sitemap_1.gz
                    Sitemap: {base_url}/sitemap_2.dat
                    Sitemap: {base_url}/sitemap_3.xml.gz
                """.format(base_url=self.TEST_BASE_URL)).strip(),
            )

            # Gzipped sitemap without correct HTTP header but with .gz extension
            m.get(
                self.TEST_BASE_URL + '/sitemap_1.gz',
                content=gzip(textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                            xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
                        <url>
                            <loc>{base_url}/news/foo.html</loc>
                            <news:news>
                                <news:publication>
                                    <news:name>{publication_name}</news:name>
                                    <news:language>{publication_language}</news:language>
                                </news:publication>
                                <news:publication_date>{publication_date}</news:publication_date>
                                <news:title>Foo &lt;foo&gt;</news:title>    <!-- HTML entity decoding -->
                            </news:news>
                        </url>
                    </urlset>
                """.format(
                    base_url=self.TEST_BASE_URL,
                    publication_name=self.TEST_PUBLICATION_NAME,
                    publication_language=self.TEST_PUBLICATION_LANGUAGE,
                    publication_date=self.TEST_DATE_STR_ISO8601,
                )).strip()),
            )

            # Gzipped sitemap with correct HTTP header but without .gz extension
            m.get(
                self.TEST_BASE_URL + '/sitemap_2.dat',
                headers={'Content-Type': 'application/x-gzip'},
                content=gzip(textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                            xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
                        <url>
                            <loc>{base_url}/news/bar.html</loc>
                            <news:news>
                                <news:publication>
                                    <news:name>{publication_name}</news:name>
                                    <news:language>{publication_language}</news:language>
                                </news:publication>
                                <news:publication_date>{publication_date}</news:publication_date>
                                <news:title><![CDATA[Bąr]]></news:title>    <!-- CDATA and UTF-8 -->
                            </news:news>
                        </url>
                    </urlset>
                """.format(
                    base_url=self.TEST_BASE_URL,
                    publication_name=self.TEST_PUBLICATION_NAME,
                    publication_language=self.TEST_PUBLICATION_LANGUAGE,
                    publication_date=self.TEST_DATE_STR_ISO8601,
                )).strip()),
            )

            # Sitemap which appears to be gzipped (due to extension and Content-Type) but really isn't
            m.get(
                self.TEST_BASE_URL + '/sitemap_3.xml.gz',
                headers={'Content-Type': 'application/x-gzip'},
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                            xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
                        <url>
                            <loc>{base_url}/news/baz.html</loc>
                            <news:news>
                                <news:publication>
                                    <news:name>{publication_name}</news:name>
                                    <news:language>{publication_language}</news:language>
                                </news:publication>
                                <news:publication_date>{publication_date}</news:publication_date>
                                <news:title><![CDATA[Bąž]]></news:title>    <!-- CDATA and UTF-8 -->
                            </news:news>
                        </url>
                    </urlset>
                """.format(
                    base_url=self.TEST_BASE_URL,
                    publication_name=self.TEST_PUBLICATION_NAME,
                    publication_language=self.TEST_PUBLICATION_LANGUAGE,
                    publication_date=self.TEST_DATE_STR_ISO8601,
                )).strip(),
            )

            actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

            # Don't do an in-depth check, we just need to make sure that gunzip works
            assert isinstance(actual_sitemap_tree, IndexWebsiteSitemap)
            assert len(actual_sitemap_tree.sub_sitemaps) == 1

            assert isinstance(actual_sitemap_tree.sub_sitemaps[0], IndexRobotsTxtSitemap)
            # noinspection PyUnresolvedReferences
            assert len(actual_sitemap_tree.sub_sitemaps[0].sub_sitemaps) == 3

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

    def test_sitemap_tree_for_homepage_plain_text(self):
        """Test sitemap_tree_for_homepage() with plain text sitemaps."""

        with requests_mock.Mocker() as m:
            m.add_matcher(TestSitemapTree.fallback_to_404_not_found_matcher)

            m.get(
                self.TEST_BASE_URL + '/',
                text='This is a homepage.',
            )

            m.get(
                self.TEST_BASE_URL + '/robots.txt',
                headers={'Content-Type': 'text/plain'},
                text=textwrap.dedent("""
                    User-agent: *
                    Disallow: /whatever
    
                    Sitemap: {base_url}/sitemap_1.txt
                    Sitemap: {base_url}/sitemap_2.txt.dat
                """.format(base_url=self.TEST_BASE_URL)).strip(),
            )

            # Plain text uncompressed sitemap (no Content-Type header)
            m.get(
                self.TEST_BASE_URL + '/sitemap_1.txt',
                text=textwrap.dedent("""
    
                    {base_url}/news/foo.html
    
    
                    {base_url}/news/bar.html
    
                    Some other stuff which totally doesn't look like an URL
                """.format(base_url=self.TEST_BASE_URL)).strip(),
            )

            # Plain text compressed sitemap without .gz extension
            m.get(
                self.TEST_BASE_URL + '/sitemap_2.txt.dat',
                headers={'Content-Type': 'application/x-gzip'},
                content=gzip(textwrap.dedent("""
                    {base_url}/news/bar.html
                        {base_url}/news/baz.html
                """.format(base_url=self.TEST_BASE_URL)).strip()),
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
            assert SitemapPage(url='{}/news/foo.html'.format(self.TEST_BASE_URL)) in pages
            assert SitemapPage(url='{}/news/bar.html'.format(self.TEST_BASE_URL)) in pages
            assert SitemapPage(url='{}/news/baz.html'.format(self.TEST_BASE_URL)) in pages

    # noinspection DuplicatedCode
    def test_sitemap_tree_for_homepage_rss_atom(self):
        """Test sitemap_tree_for_homepage() with RSS 2.0 / Atom 0.3 / Atom 1.0 feeds."""

        with requests_mock.Mocker() as m:
            m.add_matcher(TestSitemapTree.fallback_to_404_not_found_matcher)

            m.get(
                self.TEST_BASE_URL + '/',
                text='This is a homepage.',
            )

            m.get(
                self.TEST_BASE_URL + '/robots.txt',
                headers={'Content-Type': 'text/plain'},
                text=textwrap.dedent("""
                    User-agent: *
                    Disallow: /whatever

                    Sitemap: {base_url}/sitemap_rss.xml
                    Sitemap: {base_url}/sitemap_atom_0_3.xml
                    Sitemap: {base_url}/sitemap_atom_1_0.xml
                """.format(base_url=self.TEST_BASE_URL)).strip(),
            )

            # RSS 2.0 sitemap
            m.get(
                self.TEST_BASE_URL + '/sitemap_rss.xml',
                headers={'Content-Type': 'application/rss+xml'},
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <rss version="2.0">
                        <channel>
                            <title>Test RSS 2.0 feed</title>
                            <description>This is a test RSS 2.0 feed.</description>
                            <link>{base_url}</link>
                            <pubDate>{pub_date}</pubDate>

                            <item>
                                <title>Test RSS 2.0 story #1</title>
                                <description>This is a test RSS 2.0 story #1.</description>
                                <link>{base_url}/rss_story_1.html</link>
                                <guid isPermaLink="true">{base_url}/rss_story_1.html</guid>
                                <pubDate>{pub_date}</pubDate>
                            </item>

                            <item>
                                <title>Test RSS 2.0 story #2</title>
                                <description>This is a test RSS 2.0 story #2.</description>
                                <link>{base_url}/rss_story_2.html</link>
                                <guid isPermaLink="true">{base_url}/rss_story_2.html</guid>
                                <pubDate>{pub_date}</pubDate>
                            </item>

                        </channel>
                    </rss>
                """.format(base_url=self.TEST_BASE_URL, pub_date=self.TEST_DATE_STR_RFC2822)).strip(),
            )

            # Atom 0.3 sitemap
            m.get(
                self.TEST_BASE_URL + '/sitemap_atom_0_3.xml',
                headers={'Content-Type': 'application/atom+xml'},
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <feed version="0.3" xmlns="http://purl.org/atom/ns#">
                        <title>Test Atom 0.3 feed</title>
                        <link rel="alternate" type="text/html" href="{base_url}" />
                        <modified>{pub_date}</modified>

                        <entry>
                            <title>Test Atom 0.3 story #1</title>
                            <link rel="alternate" type="text/html" href="{base_url}/atom_0_3_story_1.html" />
                            <id>{base_url}/atom_0_3_story_1.html</id>
                            <issued>{pub_date}</issued>
                        </entry>

                        <entry>
                            <title>Test Atom 0.3 story #2</title>
                            <link rel="alternate" type="text/html" href="{base_url}/atom_0_3_story_2.html" />
                            <id>{base_url}/atom_0_3_story_2.html</id>
                            <issued>{pub_date}</issued>
                        </entry>

                    </feed>
                """.format(base_url=self.TEST_BASE_URL, pub_date=self.TEST_DATE_STR_ISO8601)).strip(),
            )

            # Atom 1.0 sitemap
            m.get(
                self.TEST_BASE_URL + '/sitemap_atom_1_0.xml',
                headers={'Content-Type': 'application/atom+xml'},
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <feed xmlns="http://www.w3.org/2005/Atom">
                        <title>Test Atom 1.0 feed</title>
                        <subtitle>This is a test Atom 1.0 feed.</subtitle>
                        <link href="{base_url}/sitemap_atom_1_0.xml" rel="self" />
                        <link href="{base_url}" />
                        <id>{base_url}</id>
                        <updated>{pub_date}</updated>

                        <entry>
                            <title>Test Atom 1.0 story #1</title>
                            <link href="{base_url}/atom_1_0_story_1.html" />
                            <link rel="alternate" type="text/html" href="{base_url}/atom_1_0_story_1.html?alt" />
                            <link rel="edit" href="{base_url}/atom_1_0_story_1.html?edit" />
                            <id>{base_url}/atom_1_0_story_1.html</id>
                            <updated>{pub_date}</updated>
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
                            <link href="{base_url}/atom_1_0_story_2.html" />
                            <link rel="alternate" type="text/html" href="{base_url}/atom_1_0_story_2.html?alt" />
                            <link rel="edit" href="{base_url}/atom_1_0_story_2.html?edit" />
                            <id>{base_url}/atom_1_0_story_2.html</id>
                            <updated>{pub_date}</updated>
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
                """.format(base_url=self.TEST_BASE_URL, pub_date=self.TEST_DATE_STR_ISO8601)).strip(),
            )

            expected_sitemap_tree = IndexWebsiteSitemap(
                url='{}/'.format(self.TEST_BASE_URL),
                sub_sitemaps=[
                    IndexRobotsTxtSitemap(
                        url='{}/robots.txt'.format(self.TEST_BASE_URL),
                        sub_sitemaps=[
                            PagesRSSSitemap(
                                url='{}/sitemap_rss.xml'.format(self.TEST_BASE_URL),
                                pages=[
                                    SitemapPage(
                                        url='{}/rss_story_1.html'.format(self.TEST_BASE_URL),
                                        news_story=SitemapNewsStory(
                                            title='Test RSS 2.0 story #1',
                                            publish_date=self.TEST_DATE_DATETIME,
                                        ),
                                    ),
                                    SitemapPage(
                                        url='{}/rss_story_2.html'.format(self.TEST_BASE_URL),
                                        news_story=SitemapNewsStory(
                                            title='Test RSS 2.0 story #2',
                                            publish_date=self.TEST_DATE_DATETIME,
                                        )
                                    )
                                ]
                            ),
                            PagesAtomSitemap(
                                url='{}/sitemap_atom_0_3.xml'.format(self.TEST_BASE_URL),
                                pages=[
                                    SitemapPage(
                                        url='{}/atom_0_3_story_1.html'.format(self.TEST_BASE_URL),
                                        news_story=SitemapNewsStory(
                                            title='Test Atom 0.3 story #1',
                                            publish_date=self.TEST_DATE_DATETIME,
                                        ),
                                    ),
                                    SitemapPage(
                                        url='{}/atom_0_3_story_2.html'.format(self.TEST_BASE_URL),
                                        news_story=SitemapNewsStory(
                                            title='Test Atom 0.3 story #2',
                                            publish_date=self.TEST_DATE_DATETIME,
                                        )
                                    )
                                ]
                            ),
                            PagesAtomSitemap(
                                url='{}/sitemap_atom_1_0.xml'.format(self.TEST_BASE_URL),
                                pages=[
                                    SitemapPage(
                                        url='{}/atom_1_0_story_1.html'.format(self.TEST_BASE_URL),
                                        news_story=SitemapNewsStory(
                                            title='Test Atom 1.0 story #1',
                                            publish_date=self.TEST_DATE_DATETIME,
                                        ),
                                    ),
                                    SitemapPage(
                                        url='{}/atom_1_0_story_2.html'.format(self.TEST_BASE_URL),
                                        news_story=SitemapNewsStory(
                                            title='Test Atom 1.0 story #2',
                                            publish_date=self.TEST_DATE_DATETIME,
                                        )
                                    )
                                ]
                            ),
                        ]
                    )
                ]
            )

            actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

            expected_lines = str(expected_sitemap_tree).split()
            actual_lines = str(actual_sitemap_tree).split()
            diff = difflib.ndiff(expected_lines, actual_lines)
            diff_str = '\n'.join(diff)

            assert expected_sitemap_tree == actual_sitemap_tree, diff_str

            assert len(list(actual_sitemap_tree.all_pages())) == 6

    def test_sitemap_tree_for_homepage_rss_atom_empty(self):
        """Test sitemap_tree_for_homepage() with empty RSS 2.0 / Atom 0.3 / Atom 1.0 feeds."""

        with requests_mock.Mocker() as m:
            m.add_matcher(TestSitemapTree.fallback_to_404_not_found_matcher)

            m.get(
                self.TEST_BASE_URL + '/',
                text='This is a homepage.',
            )

            m.get(
                self.TEST_BASE_URL + '/robots.txt',
                headers={'Content-Type': 'text/plain'},
                text=textwrap.dedent("""
                    User-agent: *
                    Disallow: /whatever

                    Sitemap: {base_url}/sitemap_rss.xml
                    Sitemap: {base_url}/sitemap_atom_0_3.xml
                    Sitemap: {base_url}/sitemap_atom_1_0.xml
                """.format(base_url=self.TEST_BASE_URL)).strip(),
            )

            # RSS 2.0 sitemap
            m.get(
                self.TEST_BASE_URL + '/sitemap_rss.xml',
                headers={'Content-Type': 'application/rss+xml'},
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <rss version="2.0">
                        <channel>
                            <title>Test RSS 2.0 feed</title>
                            <description>This is a test RSS 2.0 feed.</description>
                            <link>{base_url}</link>
                            <pubDate>{pub_date}</pubDate>
                        </channel>
                    </rss>
                """.format(base_url=self.TEST_BASE_URL, pub_date=self.TEST_DATE_STR_RFC2822)).strip(),
            )

            # Atom 0.3 sitemap
            m.get(
                self.TEST_BASE_URL + '/sitemap_atom_0_3.xml',
                headers={'Content-Type': 'application/atom+xml'},
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <feed version="0.3" xmlns="http://purl.org/atom/ns#">
                        <title>Test Atom 0.3 feed</title>
                        <link rel="alternate" type="text/html" href="{base_url}" />
                        <modified>{pub_date}</modified>
                    </feed>
                """.format(base_url=self.TEST_BASE_URL, pub_date=self.TEST_DATE_STR_ISO8601)).strip(),
            )

            # Atom 1.0 sitemap
            m.get(
                self.TEST_BASE_URL + '/sitemap_atom_1_0.xml',
                headers={'Content-Type': 'application/atom+xml'},
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <feed xmlns="http://www.w3.org/2005/Atom">
                        <title>Test Atom 1.0 feed</title>
                        <subtitle>This is a test Atom 1.0 feed.</subtitle>
                        <link href="{base_url}/sitemap_atom_1_0.xml" rel="self" />
                        <link href="{base_url}" />
                        <id>{base_url}</id>
                        <updated>{pub_date}</updated>
                    </feed>
                """.format(base_url=self.TEST_BASE_URL, pub_date=self.TEST_DATE_STR_ISO8601)).strip(),
            )

            expected_sitemap_tree = IndexWebsiteSitemap(
                url='{}/'.format(self.TEST_BASE_URL),
                sub_sitemaps=[
                    IndexRobotsTxtSitemap(
                        url='{}/robots.txt'.format(self.TEST_BASE_URL),
                        sub_sitemaps=[
                            PagesRSSSitemap(
                                url='{}/sitemap_rss.xml'.format(self.TEST_BASE_URL),
                                pages=[]
                            ),
                            PagesAtomSitemap(
                                url='{}/sitemap_atom_0_3.xml'.format(self.TEST_BASE_URL),
                                pages=[]
                            ),
                            PagesAtomSitemap(
                                url='{}/sitemap_atom_1_0.xml'.format(self.TEST_BASE_URL),
                                pages=[]
                            ),
                        ]
                    )
                ]
            )

            actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

            assert expected_sitemap_tree == actual_sitemap_tree

            assert len(list(actual_sitemap_tree.all_pages())) == 0

    def test_sitemap_tree_for_homepage_prematurely_ending_xml(self):
        """Test sitemap_tree_for_homepage() with clipped XML.

        Some webservers are misconfigured to limit the request length to a certain number of seconds, in which time the
        server is unable to generate and compress a 50 MB sitemap XML. Google News doesn't seem to have a problem with
        this behavior, so we have to support this too.
        """

        with requests_mock.Mocker() as m:
            m.add_matcher(TestSitemapTree.fallback_to_404_not_found_matcher)

            m.get(
                self.TEST_BASE_URL + '/',
                text='This is a homepage.',
            )

            m.get(
                self.TEST_BASE_URL + '/robots.txt',
                headers={'Content-Type': 'text/plain'},
                text=textwrap.dedent("""
                    User-agent: *
                    Disallow: /whatever
    
                    Sitemap: {base_url}/sitemap.xml
                """.format(base_url=self.TEST_BASE_URL)).strip(),
            )

            m.get(
                self.TEST_BASE_URL + '/sitemap.xml',
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                            xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
                        <url>
                            <loc>{base_url}/news/first.html</loc>
                            <news:news>
                                <news:publication>
                                    <news:name>{publication_name}</news:name>
                                    <news:language>{publication_language}</news:language>
                                </news:publication>
                                <news:publication_date>{publication_date}</news:publication_date>
                                <news:title>First story</news:title>
                            </news:news>
                        </url>
                        <url>
                            <loc>{base_url}/news/second.html</loc>
                            <news:news>
                                <news:publication>
                                    <news:name>{publication_name}</news:name>
                                    <news:language>{publication_language}</news:language>
                                </news:publication>
                                <news:publication_date>{publication_date}</news:publication_date>
                                <news:title>Second story</news:title>
                            </news:news>
                        </url>
    
                        <!-- The following story shouldn't get added as the XML ends prematurely -->
                        <url>
                            <loc>{base_url}/news/third.html</loc>
                            <news:news>
                                <news:publication>
                                    <news:name>{publication_name}</news:name>
                                    <news:language>{publication_language}</news:language>
                                </news:publication>
                                <news:publicat
                """.format(
                    base_url=self.TEST_BASE_URL,
                    publication_name=self.TEST_PUBLICATION_NAME,
                    publication_language=self.TEST_PUBLICATION_LANGUAGE,
                    publication_date=self.TEST_DATE_STR_ISO8601,
                )).strip(),
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

    def test_sitemap_tree_for_homepage_no_sitemap(self):
        """Test sitemap_tree_for_homepage() with no sitemaps listed in robots.txt."""

        with requests_mock.Mocker() as m:
            m.add_matcher(TestSitemapTree.fallback_to_404_not_found_matcher)

            m.get(
                self.TEST_BASE_URL + '/',
                text='This is a homepage.',
            )

            m.get(
                self.TEST_BASE_URL + '/robots.txt',
                headers={'Content-Type': 'text/plain'},
                text=textwrap.dedent("""
                    User-agent: *
                    Disallow: /whatever
                """.format(base_url=self.TEST_BASE_URL)).strip(),
            )

            expected_sitemap_tree = IndexWebsiteSitemap(
                url='{}/'.format(self.TEST_BASE_URL),
                sub_sitemaps=[
                    IndexRobotsTxtSitemap(
                        url='{}/robots.txt'.format(self.TEST_BASE_URL),
                        sub_sitemaps=[],
                    )
                ]
            )

            actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

            assert expected_sitemap_tree == actual_sitemap_tree

    def test_sitemap_tree_for_homepage_unpublished_sitemap(self):
        """Test sitemap_tree_for_homepage() with some sitemaps not published in robots.txt."""

        with requests_mock.Mocker() as m:
            m.add_matcher(TestSitemapTree.fallback_to_404_not_found_matcher)

            m.get(
                self.TEST_BASE_URL + '/',
                text='This is a homepage.',
            )

            m.get(
                self.TEST_BASE_URL + '/robots.txt',
                headers={'Content-Type': 'text/plain'},
                text=textwrap.dedent("""
                    User-agent: *
                    Disallow: /whatever
                    
                    Sitemap: {base_url}/sitemap_public.xml
                """.format(base_url=self.TEST_BASE_URL)).strip(),
            )

            # Public sitemap (linked to from robots.txt)
            m.get(
                self.TEST_BASE_URL + '/sitemap_public.xml',
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                        <url>
                            <loc>{base_url}/news/public.html</loc>
                        </url>
                    </urlset>
                """.format(
                    base_url=self.TEST_BASE_URL,
                    publication_name=self.TEST_PUBLICATION_NAME,
                    publication_language=self.TEST_PUBLICATION_LANGUAGE,
                    publication_date=self.TEST_DATE_STR_ISO8601,
                )).strip(),
            )

            # Private sitemap (to be discovered by trying out a few paths)
            m.get(
                self.TEST_BASE_URL + '/sitemap_index.xml',
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                        <url>
                            <loc>{base_url}/news/private.html</loc>
                        </url>
                    </urlset>
                """.format(
                    base_url=self.TEST_BASE_URL,
                    publication_name=self.TEST_PUBLICATION_NAME,
                    publication_language=self.TEST_PUBLICATION_LANGUAGE,
                    publication_date=self.TEST_DATE_STR_ISO8601,
                )).strip(),
            )

            expected_sitemap_tree = IndexWebsiteSitemap(
                url='{}/'.format(self.TEST_BASE_URL),
                sub_sitemaps=[
                    IndexRobotsTxtSitemap(
                        url='{}/robots.txt'.format(self.TEST_BASE_URL),
                        sub_sitemaps=[
                            PagesXMLSitemap(
                                url='{}/sitemap_public.xml'.format(self.TEST_BASE_URL),
                                pages=[
                                    SitemapPage(
                                        url='{}/news/public.html'.format(self.TEST_BASE_URL),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    PagesXMLSitemap(
                        url='{}/sitemap_index.xml'.format(self.TEST_BASE_URL),
                        pages=[
                            SitemapPage(
                                url='{}/news/private.html'.format(self.TEST_BASE_URL),
                            ),
                        ],
                    ),
                ]
            )

            actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

            assert expected_sitemap_tree == actual_sitemap_tree

    def test_sitemap_tree_for_homepage_robots_txt_no_content_type(self):
        """Test sitemap_tree_for_homepage() with no Content-Type in robots.txt."""

        with requests_mock.Mocker() as m:
            m.add_matcher(TestSitemapTree.fallback_to_404_not_found_matcher)

            m.get(
                self.TEST_BASE_URL + '/',
                text='This is a homepage.',
            )

            m.get(
                self.TEST_BASE_URL + '/robots.txt',
                headers={'Content-Type': ''},
                text=textwrap.dedent("""
                    User-agent: *
                    Disallow: /whatever
                """.format(base_url=self.TEST_BASE_URL)).strip(),
            )

            expected_sitemap_tree = IndexWebsiteSitemap(
                url='{}/'.format(self.TEST_BASE_URL),
                sub_sitemaps=[
                    IndexRobotsTxtSitemap(
                        url='{}/robots.txt'.format(self.TEST_BASE_URL),
                        sub_sitemaps=[],
                    )
                ]
            )

            actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

            assert expected_sitemap_tree == actual_sitemap_tree

    def test_sitemap_tree_for_homepage_no_robots_txt(self):
        """Test sitemap_tree_for_homepage() with no robots.txt."""

        with requests_mock.Mocker() as m:
            m.add_matcher(TestSitemapTree.fallback_to_404_not_found_matcher)

            m.get(
                self.TEST_BASE_URL + '/',
                text='This is a homepage.',
            )

            # Nonexistent robots.txt
            m.get(
                self.TEST_BASE_URL + '/robots.txt',
                status_code=404,
                reason='Not Found',
                headers={'Content-Type': 'text/html'},
                text="<h1>404 Not Found!</h1>",
            )

            expected_sitemap_tree = IndexWebsiteSitemap(
                url='{}/'.format(self.TEST_BASE_URL),
                sub_sitemaps=[],
            )

            actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

            assert expected_sitemap_tree == actual_sitemap_tree

    def test_sitemap_tree_for_homepage_huge_sitemap(self):
        """Test sitemap_tree_for_homepage() with a huge sitemap (mostly for profiling)."""

        page_count = 1000

        sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
            <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                    xmlns:news="http://www.google.com/schemas/sitemap-news/0.9"
                    xmlns:xhtml="http://www.w3.org/1999/xhtml">
        """
        for x in range(page_count):
            sitemap_xml += """
                <url>
                    <loc>{base_url}/news/page_{x}.html</loc>

                    <!-- Element present but empty -->
                    <lastmod />

                    <!-- Some other XML namespace -->
                    <xhtml:link rel="alternate"
                                media="only screen and (max-width: 640px)"
                                href="{base_url}/news/page_{x}.html?mobile=1" />

                    <news:news>
                        <news:publication>
                            <news:name>{publication_name}</news:name>
                            <news:language>{publication_language}</news:language>
                        </news:publication>
                        <news:publication_date>{publication_date}</news:publication_date>
                        <news:title>Foo &lt;foo&gt;</news:title>    <!-- HTML entity decoding -->
                    </news:news>
                </url>
            """.format(
                x=x,
                base_url=self.TEST_BASE_URL,
                publication_name=self.TEST_PUBLICATION_NAME,
                publication_language=self.TEST_PUBLICATION_LANGUAGE,
                publication_date=self.TEST_DATE_STR_ISO8601,
            )

        sitemap_xml += "</urlset>"

        with requests_mock.Mocker() as m:
            m.add_matcher(TestSitemapTree.fallback_to_404_not_found_matcher)

            m.get(
                self.TEST_BASE_URL + '/',
                text='This is a homepage.',
            )

            m.get(
                self.TEST_BASE_URL + '/robots.txt',
                headers={'Content-Type': 'text/plain'},
                text=textwrap.dedent("""
                    User-agent: *
                    Disallow: /whatever
    
                    Sitemap: {base_url}/sitemap.xml.gz
                """.format(base_url=self.TEST_BASE_URL)).strip(),
            )

            m.get(
                self.TEST_BASE_URL + '/sitemap.xml.gz',
                headers={'Content-Type': 'application/x-gzip'},
                content=gzip(sitemap_xml),
            )

            actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

            assert len(list(actual_sitemap_tree.all_pages())) == page_count

    def test_sitemap_tree_for_homepage_robots_txt_weird_spacing(self):
        """Test sitemap_tree_for_homepage() with weird (but valid) spacing."""

        with requests_mock.Mocker() as m:
            m.add_matcher(TestSitemapTree.fallback_to_404_not_found_matcher)

            m.get(
                self.TEST_BASE_URL + '/',
                text='This is a homepage.',
            )

            robots_txt_body = ""
            robots_txt_body += "User-agent: *\n"
            # Extra space before "Sitemap:", no space after "Sitemap:", and extra space after sitemap URL
            robots_txt_body += " Sitemap:{base_url}/sitemap.xml    ".format(base_url=self.TEST_BASE_URL)

            m.get(
                self.TEST_BASE_URL + '/robots.txt',
                headers={'Content-Type': 'text/plain'},
                text=robots_txt_body,
            )

            m.get(
                self.TEST_BASE_URL + '/sitemap.xml',
                text=textwrap.dedent("""
                    <?xml version="1.0" encoding="UTF-8"?>
                    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                            xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
                        <url>
                            <loc>{base_url}/news/first.html</loc>
                            <news:news>
                                <news:publication>
                                    <news:name>{publication_name}</news:name>
                                    <news:language>{publication_language}</news:language>
                                </news:publication>
                                <news:publication_date>{publication_date}</news:publication_date>
                                <news:title>First story</news:title>
                            </news:news>
                        </url>
                    </urlset>
                """.format(
                    base_url=self.TEST_BASE_URL,
                    publication_name=self.TEST_PUBLICATION_NAME,
                    publication_language=self.TEST_PUBLICATION_LANGUAGE,
                    publication_date=self.TEST_DATE_STR_ISO8601,
                )).strip(),
            )

            actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)
            assert len(list(actual_sitemap_tree.all_pages())) == 1

    def test_sitemap_tree_for_homepage_utf8_bom(self):
        """Test sitemap_tree_for_homepage() with UTF-8 BOM in both robots.txt and sitemap."""

        robots_txt_body = textwrap.dedent("""
            User-agent: *
            Disallow: /whatever

            Sitemap: {base_url}/sitemap.xml
        """.format(base_url=self.TEST_BASE_URL)).strip()

        sitemap_xml_body = textwrap.dedent("""
            <?xml version="1.0" encoding="UTF-8"?>
            <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                    xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">
                <url>
                    <loc>{base_url}/news/first.html</loc>
                    <news:news>
                        <news:publication>
                            <news:name>{publication_name}</news:name>
                            <news:language>{publication_language}</news:language>
                        </news:publication>
                        <news:publication_date>{publication_date}</news:publication_date>
                        <news:title>First story</news:title>
                    </news:news>
                </url>
            </urlset>
        """.format(
            base_url=self.TEST_BASE_URL,
            publication_name=self.TEST_PUBLICATION_NAME,
            publication_language=self.TEST_PUBLICATION_LANGUAGE,
            publication_date=self.TEST_DATE_STR_ISO8601,
        )).strip()

        robots_txt_body_encoded = robots_txt_body.encode('utf-8-sig')
        sitemap_xml_body_encoded = sitemap_xml_body.encode('utf-8-sig')

        with requests_mock.Mocker() as m:
            m.add_matcher(TestSitemapTree.fallback_to_404_not_found_matcher)

            m.get(
                self.TEST_BASE_URL + '/',
                text='This is a homepage.',
            )

            m.get(
                self.TEST_BASE_URL + '/robots.txt',
                headers={'Content-Type': 'text/plain'},
                content=robots_txt_body_encoded,
            )

            m.get(
                self.TEST_BASE_URL + '/sitemap.xml',
                content=sitemap_xml_body_encoded,
            )

            actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)
            assert len(list(actual_sitemap_tree.all_pages())) == 1
