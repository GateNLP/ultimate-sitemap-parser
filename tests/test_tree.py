import datetime
import textwrap
from decimal import Decimal
from unittest import TestCase

import dateutil
import httpretty

from tests.helpers import gzip
from usp.log import create_logger
from usp.objects import (
    IndexRobotsTxtSitemap,
    PagesXMLSitemap,
    IndexXMLSitemap,
    SitemapPage,
    InvalidSitemap,
    SitemapNewsStory,
    SitemapPageChangeFrequency,
    PagesTextSitemap,
)
from usp.tree import sitemap_tree_for_homepage

# FIXME various exotic properties
# FIXME XML vulnerabilities with Expat
# FIXME max. recursion level
# FIXME tests responses that are too big


log = create_logger(__name__)


class TestSitemapTree(TestCase):
    TEST_BASE_URL = 'http://test_ultimate_sitemap_parser.com'  # mocked by HTTPretty

    # Publication / "last modified" date
    TEST_DATE_DATETIME = datetime.datetime(
        year=2009, month=12, day=17, hour=12, minute=4, second=56,
        tzinfo=dateutil.tz.tzoffset(None, 7200),
    )
    TEST_DATE_STR = TEST_DATE_DATETIME.isoformat()

    TEST_PUBLICATION_NAME = 'Test publication'
    TEST_PUBLICATION_LANGUAGE = 'en'

    def setUp(self):
        super().setUp()

        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        httpretty.reset()

        super().tearDown()

    def test_sitemap_tree_for_homepage(self):
        """Test sitemap_tree_for_homepage()."""

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/',
            body='This is a homepage.',
        )

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/robots.txt',
            adding_headers={'Content-Type': 'text/plain'},
            body=textwrap.dedent("""
                User-agent: *
                Disallow: /whatever

                Sitemap: {base_url}/sitemap_pages.xml
                Sitemap: {base_url}/sitemap_news_index_1.xml
            """.format(base_url=self.TEST_BASE_URL)).strip(),
        )

        # One sitemap for random static pages
        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/sitemap_pages.xml',
            adding_headers={'Content-Type': 'application/xml'},
            body=textwrap.dedent("""
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
            """.format(base_url=self.TEST_BASE_URL, last_modified_date=self.TEST_DATE_STR)).strip(),
        )

        # Index sitemap pointing to sitemaps with stories
        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/sitemap_news_index_1.xml',
            adding_headers={'Content-Type': 'application/xml'},
            body=textwrap.dedent("""
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
            """.format(base_url=self.TEST_BASE_URL, last_modified=self.TEST_DATE_STR)).strip(),
        )

        # First sitemap with actual stories
        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/sitemap_news_1.xml',
            adding_headers={'Content-Type': 'application/xml'},
            body=textwrap.dedent("""
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
                publication_date=self.TEST_DATE_STR,
            )).strip(),
        )

        # Another index sitemap pointing to a second sitemaps with stories
        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/sitemap_news_index_2.xml',
            adding_headers={'Content-Type': 'application/xml'},
            body=textwrap.dedent("""
                <?xml version="1.0" encoding="UTF-8"?>
                <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">

                    <sitemap>
                        <!-- Extra whitespace added around URL -->
                        <loc>  {base_url}/sitemap_news_2.xml  </loc>
                        <lastmod>{last_modified}</lastmod>
                    </sitemap>

                    <!-- Nonexistent sitemap -->
                    <sitemap>
                        <loc>{base_url}/sitemap_news_nonexistent.xml</loc>
                        <lastmod>{last_modified}</lastmod>
                    </sitemap>

                </sitemapindex>
            """.format(base_url=self.TEST_BASE_URL, last_modified=self.TEST_DATE_STR)).strip(),
        )

        # Second sitemap with actual stories
        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/sitemap_news_2.xml',
            adding_headers={'Content-Type': 'application/xml'},
            body=textwrap.dedent("""
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
                publication_date=self.TEST_DATE_STR,
            )).strip(),
        )

        # Nonexistent sitemap
        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/sitemap_news_nonexistent.xml',
            status=404,
            adding_headers={'Content-Type': 'text/html'},
            body="<h1>404 Not Found!</h1>"
        )

        # noinspection PyArgumentList
        expected_sitemap_tree = IndexRobotsTxtSitemap(
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
                                    url='{}/sitemap_news_nonexistent.xml'.format(self.TEST_BASE_URL),
                                    reason=(
                                        'Unable to fetch sitemap from {base_url}/sitemap_news_nonexistent.xml: '
                                        '404 Not Found'
                                    ).format(base_url=self.TEST_BASE_URL),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        # PyCharm is not that great at formatting object diffs, so uncomment the following and set a breakpoint:
        #
        # expected_lines = str(expected_sitemap_tree).split()
        # actual_lines = str(actual_sitemap_tree).split()
        # diff = difflib.ndiff(expected_lines, actual_lines)
        # diff_str = '\n'.join(diff)
        # assert expected_lines == actual_lines

        assert expected_sitemap_tree == actual_sitemap_tree

        assert len(actual_sitemap_tree.all_pages()) == 5

    def test_sitemap_tree_for_homepage_gzip(self):
        """Test sitemap_tree_for_homepage() with gzipped sitemaps."""

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/',
            body='This is a homepage.',
        )

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/robots.txt',
            adding_headers={'Content-Type': 'text/plain'},
            body=textwrap.dedent("""
                User-agent: *
                Disallow: /whatever

                Sitemap: {base_url}/sitemap_1.gz
                Sitemap: {base_url}/sitemap_2.dat
            """.format(base_url=self.TEST_BASE_URL)).strip(),
        )

        # Gzipped sitemap without correct HTTP header but with .gz extension
        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/sitemap_1.gz',
            body=gzip(textwrap.dedent("""
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
                publication_date=self.TEST_DATE_STR,
            )).strip()),
        )

        # Gzipped sitemap with correct HTTP header but without .gz extension
        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/sitemap_2.dat',
            adding_headers={'Content-Type': 'application/x-gzip'},
            body=gzip(textwrap.dedent("""
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
                publication_date=self.TEST_DATE_STR,
            )).strip()),
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        # Don't do an in-depth check, we just need to make sure that gunzip works
        assert isinstance(actual_sitemap_tree, IndexRobotsTxtSitemap)
        assert len(actual_sitemap_tree.sub_sitemaps) == 2

        sitemap_1 = actual_sitemap_tree.sub_sitemaps[0]
        assert isinstance(sitemap_1, PagesXMLSitemap)
        assert len(sitemap_1.pages) == 1

        sitemap_2 = actual_sitemap_tree.sub_sitemaps[1]
        assert isinstance(sitemap_2, PagesXMLSitemap)
        assert len(sitemap_2.pages) == 1

    def test_sitemap_tree_for_homepage_plain_text(self):
        """Test sitemap_tree_for_homepage() with plain text sitemaps."""

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/',
            body='This is a homepage.',
        )

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/robots.txt',
            adding_headers={'Content-Type': 'text/plain'},
            body=textwrap.dedent("""
                User-agent: *
                Disallow: /whatever

                Sitemap: {base_url}/sitemap_1.txt
                Sitemap: {base_url}/sitemap_2.txt.dat
            """.format(base_url=self.TEST_BASE_URL)).strip(),
        )

        # Plain text uncompressed sitemap (no Content-Type header)
        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/sitemap_1.txt',
            body=textwrap.dedent("""

                {base_url}/news/foo.html


                {base_url}/news/bar.html

                Some other stuff which totally doesn't look like an URL
            """.format(base_url=self.TEST_BASE_URL)).strip(),
        )

        # Plain text compressed sitemap without .gz extension
        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/sitemap_2.txt.dat',
            adding_headers={'Content-Type': 'application/x-gzip'},
            body=gzip(textwrap.dedent("""
                {base_url}/news/bar.html
                    {base_url}/news/baz.html
            """.format(base_url=self.TEST_BASE_URL)).strip()),
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        assert isinstance(actual_sitemap_tree, IndexRobotsTxtSitemap)
        assert len(actual_sitemap_tree.sub_sitemaps) == 2

        sitemap_1 = actual_sitemap_tree.sub_sitemaps[0]
        assert isinstance(sitemap_1, PagesTextSitemap)
        assert len(sitemap_1.pages) == 2

        sitemap_2 = actual_sitemap_tree.sub_sitemaps[1]
        assert isinstance(sitemap_2, PagesTextSitemap)
        assert len(sitemap_2.pages) == 2

        pages = actual_sitemap_tree.all_pages()
        assert len(pages) == 3
        print(pages)
        assert SitemapPage(url='{}/news/foo.html'.format(self.TEST_BASE_URL)) in pages
        assert SitemapPage(url='{}/news/bar.html'.format(self.TEST_BASE_URL)) in pages
        assert SitemapPage(url='{}/news/baz.html'.format(self.TEST_BASE_URL)) in pages

    def test_sitemap_tree_for_homepage_prematurely_ending_xml(self):
        """Test sitemap_tree_for_homepage() with clipped XML.

        Some webservers are misconfigured to limit the request length to a certain number of seconds, in which time the
        server is unable to generate and compress a 50 MB sitemap XML. Google News doesn't seem to have a problem with
        this behavior, so we have to support this too.
        """

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/',
            body='This is a homepage.',
        )

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/robots.txt',
            adding_headers={'Content-Type': 'text/plain'},
            body=textwrap.dedent("""
                User-agent: *
                Disallow: /whatever

                Sitemap: {base_url}/sitemap.xml
            """.format(base_url=self.TEST_BASE_URL)).strip(),
        )

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/sitemap.xml',
            body=textwrap.dedent("""
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
                publication_date=self.TEST_DATE_STR,
            )).strip(),
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        assert isinstance(actual_sitemap_tree, IndexRobotsTxtSitemap)
        assert len(actual_sitemap_tree.sub_sitemaps) == 1

        sitemap = actual_sitemap_tree.sub_sitemaps[0]
        assert isinstance(sitemap, PagesXMLSitemap)
        assert len(sitemap.pages) == 2

    def test_sitemap_tree_for_homepage_no_sitemap(self):
        """Test sitemap_tree_for_homepage() with no sitemaps listed in robots.txt."""

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/',
            body='This is a homepage.',
        )

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/robots.txt',
            adding_headers={'Content-Type': 'text/plain'},
            body=textwrap.dedent("""
                User-agent: *
                Disallow: /whatever
            """.format(base_url=self.TEST_BASE_URL)).strip(),
        )

        # noinspection PyArgumentList
        expected_sitemap_tree = IndexRobotsTxtSitemap(
            url='{}/robots.txt'.format(self.TEST_BASE_URL),
            sub_sitemaps=[],
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        assert expected_sitemap_tree == actual_sitemap_tree

    def test_sitemap_tree_for_homepage_robots_txt_no_content_type(self):
        """Test sitemap_tree_for_homepage() with no Content-Type in robots.txt."""

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/',
            body='This is a homepage.',
        )

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/robots.txt',
            adding_headers={'Content-Type': ''},
            body=textwrap.dedent("""
                User-agent: *
                Disallow: /whatever
            """.format(base_url=self.TEST_BASE_URL)).strip(),
        )

        # noinspection PyArgumentList
        expected_sitemap_tree = IndexRobotsTxtSitemap(
            url='{}/robots.txt'.format(self.TEST_BASE_URL),
            sub_sitemaps=[],
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        assert expected_sitemap_tree == actual_sitemap_tree

    def test_sitemap_tree_for_homepage_no_robots_txt(self):
        """Test sitemap_tree_for_homepage() with no robots.txt."""

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/',
            body='This is a homepage.',
        )

        # Nonexistent robots.txt
        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/robots.txt',
            status=404,
            adding_headers={'Content-Type': 'text/html'},
            body="<h1>404 Not Found!</h1>"
        )

        # noinspection PyArgumentList
        expected_sitemap_tree = InvalidSitemap(
            url='{}/robots.txt'.format(self.TEST_BASE_URL),
            reason=(
                'Unable to fetch sitemap from {base_url}/robots.txt: 404 Not Found'
            ).format(base_url=self.TEST_BASE_URL),
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
                publication_date=self.TEST_DATE_STR,
            )

        sitemap_xml += "</urlset>"

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/',
            body='This is a homepage.',
        )

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/robots.txt',
            adding_headers={'Content-Type': 'text/plain'},
            body=textwrap.dedent("""
                User-agent: *
                Disallow: /whatever

                Sitemap: {base_url}/sitemap.xml.gz
            """.format(base_url=self.TEST_BASE_URL)).strip(),
        )

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/sitemap.xml.gz',
            adding_headers={'Content-Type': 'application/x-gzip'},
            body=gzip(sitemap_xml),
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)

        assert len(actual_sitemap_tree.all_pages()) == page_count

    def test_sitemap_tree_for_homepage_robots_txt_weird_spacing(self):
        """Test sitemap_tree_for_homepage() with weird (but valid) spacing."""

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/',
            body='This is a homepage.',
        )

        robots_txt_body = ""
        robots_txt_body += "User-agent: *\n"
        # Extra space before "Sitemap:", no space after "Sitemap:", and extra space after sitemap URL
        robots_txt_body += " Sitemap:{base_url}/sitemap.xml    ".format(base_url=self.TEST_BASE_URL)

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/robots.txt',
            adding_headers={'Content-Type': 'text/plain'},
            body=robots_txt_body,
        )

        httpretty.register_uri(
            httpretty.GET,
            self.TEST_BASE_URL + '/sitemap.xml',
            body=textwrap.dedent("""
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
                publication_date=self.TEST_DATE_STR,
            )).strip(),
        )

        actual_sitemap_tree = sitemap_tree_for_homepage(homepage_url=self.TEST_BASE_URL)
        assert len(actual_sitemap_tree.all_pages()) == 1
