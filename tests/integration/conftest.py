import json
from pathlib import Path

import pytest
import vcr


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: mark test as an integration test")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--integration"):
        return
    else:
        skip_perf = pytest.mark.skip(reason="need --integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_perf)

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
