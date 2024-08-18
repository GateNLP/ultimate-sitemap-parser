import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--integration", action="store_true", default=False, help="run integration tests"
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