import datetime
import os
import pickle
from decimal import Decimal

import pytest
from dateutil.tz import tzoffset

from tests.tree.base import TreeTestBase
from usp.tree import sitemap_tree_for_homepage


class TestTreeSave(TreeTestBase):
    @pytest.fixture
    def tree(self, requests_mock):
        self.init_basic_sitemap(requests_mock)

        return sitemap_tree_for_homepage(self.TEST_BASE_URL)

    def test_pickle(self, tree, tmp_path):
        with open(tmp_path / "sitemap.pickle", "wb") as f:
            pickle.dump(tree, f)

        tree_all_pages = list(tree.all_pages())

        # Delete the temp file without deleting the object
        os.unlink(
            tree.sub_sitemaps[0]
            .sub_sitemaps[0]
            ._AbstractPagesSitemap__pages_temp_file_path
        )

        with open(tmp_path / "sitemap.pickle", "rb") as f:
            tree_loaded = pickle.load(f)

        assert tree_all_pages == list(tree_loaded.all_pages())
        assert len(list(tree_loaded.all_sitemaps())) == 7

    def test_tree_to_dict(self, tree):
        tree_d = tree.to_dict()

        assert len(tree_d["sub_sitemaps"][0]["sub_sitemaps"][0]["pages"]) == 2
        assert "pages" not in tree_d["sub_sitemaps"][0], "index sitemap has pages key"
        assert "sub_sitemaps" not in tree_d["sub_sitemaps"][0]["sub_sitemaps"][0], (
            "page sitemap has sub_sitemaps key"
        )

    def test_page_to_dict(self, tree):
        pages = list(tree.all_pages())

        pages_d = [page.to_dict() for page in pages]

        assert pages_d == [
            {
                "url": f"{self.TEST_BASE_URL}/about.html",
                "priority": Decimal("0.8"),
                "last_modified": datetime.datetime(
                    2009, 12, 17, 12, 4, 56, tzinfo=tzoffset(None, 7200)
                ),
                "change_frequency": "monthly",
                "images": None,
                "news_story": None,
            },
            {
                "url": f"{self.TEST_BASE_URL}/contact.html",
                "priority": Decimal("0.5"),
                "last_modified": datetime.datetime(
                    2009, 12, 17, 12, 4, 56, tzinfo=tzoffset(None, 7200)
                ),
                "change_frequency": "always",
                "images": None,
                "news_story": None,
            },
            {
                "url": f"{self.TEST_BASE_URL}/news/foo.html",
                "priority": Decimal("0.5"),
                "last_modified": None,
                "change_frequency": None,
                "images": None,
                "news_story": {
                    "title": "Foo <foo>",
                    "publish_date": datetime.datetime(
                        2009, 12, 17, 12, 4, 56, tzinfo=tzoffset(None, 7200)
                    ),
                    "publication_name": "Test publication",
                    "publication_language": "en",
                    "access": None,
                    "genres": [],
                    "keywords": [],
                    "stock_tickers": [],
                },
            },
            {
                "url": f"{self.TEST_BASE_URL}/news/bar.html",
                "priority": Decimal("0.5"),
                "last_modified": None,
                "change_frequency": None,
                "images": None,
                "news_story": {
                    "title": "Bar & bar",
                    "publish_date": datetime.datetime(
                        2009, 12, 17, 12, 4, 56, tzinfo=tzoffset(None, 7200)
                    ),
                    "publication_name": "Test publication",
                    "publication_language": "en",
                    "access": None,
                    "genres": [],
                    "keywords": [],
                    "stock_tickers": [],
                },
            },
            {
                "url": f"{self.TEST_BASE_URL}/news/bar.html",
                "priority": Decimal("0.5"),
                "last_modified": None,
                "change_frequency": None,
                "images": None,
                "news_story": {
                    "title": "Bar & bar",
                    "publish_date": datetime.datetime(
                        2009, 12, 17, 12, 4, 56, tzinfo=tzoffset(None, 7200)
                    ),
                    "publication_name": "Test publication",
                    "publication_language": "en",
                    "access": None,
                    "genres": [],
                    "keywords": [],
                    "stock_tickers": [],
                },
            },
            {
                "url": f"{self.TEST_BASE_URL}/news/baz.html",
                "priority": Decimal("0.5"),
                "last_modified": None,
                "change_frequency": None,
                "images": None,
                "news_story": {
                    "title": "Bąž",
                    "publish_date": datetime.datetime(
                        2009, 12, 17, 12, 4, 56, tzinfo=tzoffset(None, 7200)
                    ),
                    "publication_name": "Test publication",
                    "publication_language": "en",
                    "access": None,
                    "genres": [],
                    "keywords": [],
                    "stock_tickers": [],
                },
            },
        ]
