import json
from pathlib import Path

import pytest
import vcr

from usp.tree import sitemap_tree_for_homepage


def pytest_generate_tests(metafunc):
    # cassettes = list(Path(__file__).parent.joinpath('cassettes').glob('*.yaml'))
    # cassette_names = [f"integration-{cassette.stem}" for cassette in cassettes]
    # metafunc.parametrize('cassette_path', cassettes, ids=cassette_names, indirect=True)
    cassettes_root = Path(__file__).parent / "cassettes"

    manifest_path = cassettes_root / "manifest.json"
    if not manifest_path.exists():
        return

    manifest = json.loads(manifest_path.read_text())
    cassette_fixtures = [
        (url, cassettes_root / item["name"]) for url, item in manifest.items()
    ]
    cassette_ids = [f"integration-{url}" for url, _ in cassette_fixtures]
    metafunc.parametrize("site_url,cassette_path", cassette_fixtures, ids=cassette_ids)


@pytest.fixture
def _with_vcr(cassette_path):
    with vcr.use_cassette(cassette_path, record_mode="none"):
        yield


@pytest.mark.usefixtures("_with_vcr")
@pytest.mark.integration
def test_integration(site_url, cassette_path):
    print(f"Loading {cassette_path}")
    sitemap = sitemap_tree_for_homepage(site_url)

    # Do this over converting to a list() as this will load all pages into memory
    # That would always be the largest memory use so would prevent measurement of the mid-process memory use
    page_count = 0
    for page in sitemap.all_pages():
        page_count += 1
    print(f"Site {site_url} has {page_count} pages")
