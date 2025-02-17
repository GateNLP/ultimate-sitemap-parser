from unittest import mock

import pytest

from tests.tree.base import TreeTestBase
from usp.tree import sitemap_tree_for_homepage


class TestTreeOpts(TreeTestBase):
    @pytest.fixture
    def mock_fetcher(self, mocker):
        return mocker.patch("usp.tree.SitemapFetcher")

    def test_extra_known_paths(self, mock_fetcher):
        sitemap_tree_for_homepage("https://example.org", extra_known_paths={"custom_sitemap.xml"})
        mock_fetcher.assert_any_call(url="https://example.org/custom_sitemap.xml", web_client=mock.ANY, recursion_level=0)
