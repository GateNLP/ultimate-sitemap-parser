import re
from unittest import mock

import pytest

from tests.tree.base import TreeTestBase
from usp.tree import sitemap_tree_for_homepage


class TestTreeOpts(TreeTestBase):
    @pytest.fixture
    def mock_fetcher(self, mocker):
        return mocker.patch("usp.tree.SitemapFetcher")

    def test_extra_known_paths(self, mock_fetcher):
        sitemap_tree_for_homepage(
            "https://example.org", extra_known_paths={"custom_sitemap.xml"}
        )
        mock_fetcher.assert_any_call(
            url="https://example.org/custom_sitemap.xml",
            web_client=mock.ANY,
            recursion_level=0,
            parent_urls=set(),
            quiet_404=True,
            recurse_callback=None,
            recurse_list_callback=None,
        )

    def test_filter_callback(self, requests_mock):
        self.init_basic_sitemap(requests_mock)

        def recurse_callback(
            url: str, recursion_level: int, parent_urls: set[str]
        ) -> bool:
            return re.search(r"news_\d", url) is None

        tree = sitemap_tree_for_homepage(
            self.TEST_BASE_URL, recurse_callback=recurse_callback
        )

        # robots, pages, news_index_1, news_index_2, missing
        assert len(list(tree.all_sitemaps())) == 5
        assert all("/news/" not in page.url for page in tree.all_pages())

    def test_filter_list_callback(self, requests_mock):
        self.init_basic_sitemap(requests_mock)

        def recurse_list_callback(
            urls: list[str], recursion_level: int, parent_urls: set[str]
        ) -> list[str]:
            return [url for url in urls if re.search(r"news_\d", url) is None]

        tree = sitemap_tree_for_homepage(
            self.TEST_BASE_URL, recurse_list_callback=recurse_list_callback
        )

        # robots, pages, news_index_1, news_index_2, missing
        assert len(list(tree.all_sitemaps())) == 5
        assert all("/news/" not in page.url for page in tree.all_pages())

    def test_normalize_homepage_url_default_enabled(self, mock_fetcher):
        """
        By default, the homepage URL is normalized to the domain root.
        robots.txt should be requested from the domain root.
        """
        sitemap_tree_for_homepage("https://example.org/foo/bar")

        mock_fetcher.assert_any_call(
            url="https://example.org/robots.txt",
            web_client=mock.ANY,
            recursion_level=0,
            parent_urls=set(),
            recurse_callback=None,
            recurse_list_callback=None,
        )

    def test_normalize_homepage_url_disabled(self, mock_fetcher):
        """
        When normalize_homepage_url=False, the provided path is preserved.
        robots.txt should be requested relative to the original path.
        """
        sitemap_tree_for_homepage(
            "https://example.org/foo/bar",
            normalize_homepage_url=False,
        )

        mock_fetcher.assert_any_call(
            url="https://example.org/foo/bar/robots.txt",
            web_client=mock.ANY,
            recursion_level=0,
            parent_urls=set(),
            recurse_callback=None,
            recurse_list_callback=None,
        )

    def test_normalize_homepage_url_with_extra_known_paths(self, mock_fetcher):
        """
        When normalize_homepage_url=False, extra_known_paths are correctly appended
        to the provided path instead of the domain root.
        """
        sitemap_tree_for_homepage(
            "https://example.org/foo/bar",
            normalize_homepage_url=False,
            extra_known_paths={"custom_sitemap.xml", "another/path.xml"},
        )

        mock_fetcher.assert_any_call(
            url="https://example.org/foo/bar/custom_sitemap.xml",
            web_client=mock.ANY,
            recursion_level=0,
            parent_urls=set(),
            quiet_404=True,
            recurse_callback=None,
            recurse_list_callback=None,
        )

        mock_fetcher.assert_any_call(
            url="https://example.org/foo/bar/another/path.xml",
            web_client=mock.ANY,
            recursion_level=0,
            parent_urls=set(),
            quiet_404=True,
            recurse_callback=None,
            recurse_list_callback=None,
        )

    def test_skip_robots_txt(self, mock_fetcher):
        """
        When use_robots=False, robots.txt is not fetched at all.
        Sitemaps should be discovered relative to the provided homepage URL.
        """
        sitemap_tree_for_homepage(
            "https://example.org/foo/bar",
            use_robots=False,
            normalize_homepage_url=False,
        )

        # extra_known_paths should still be requested relative to the original path
        mock_fetcher.assert_any_call(
            url="https://example.org/foo/bar/sitemap.xml",
            web_client=mock.ANY,
            recursion_level=0,
            parent_urls=set(),
            quiet_404=True,
            recurse_callback=None,
            recurse_list_callback=None,
        )
