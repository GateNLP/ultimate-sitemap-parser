"""
This test loads all pages into a list for testing memory consumption.
"""

import pytest

from usp.tree import sitemap_tree_for_homepage


@pytest.mark.usefixtures("_with_vcr")
@pytest.mark.integration
def test_all_page_size(site_url, cassette_path):
    print(f"Loading {cassette_path}")
    sitemap = sitemap_tree_for_homepage(site_url)
    pages = list(sitemap.all_pages())
    print(f"Site {site_url} has {len(pages)} pages")
