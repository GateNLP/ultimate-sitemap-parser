import logging

import pytest

from usp.tree import sitemap_tree_for_homepage


@pytest.mark.usefixtures("_with_vcr")
@pytest.mark.integration
def test_sitemap_parse(site_url, cassette_path):
    logging.critical(f"Loading {cassette_path}")
    sitemap = sitemap_tree_for_homepage(site_url)

    # Do this over converting to a list() as this will load all pages into memory
    # That would always be the largest memory use so would prevent measurement of the mid-process memory use
    page_count = 0
    for page in sitemap.all_pages():
        page_count += 1
    logging.critical(f"Site {site_url} has {page_count} pages")
