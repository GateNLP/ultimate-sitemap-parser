import datetime
from email.utils import format_datetime

from dateutil.tz import tzoffset
import requests_mock as rq_mock


class TreeTestBase:
    TEST_BASE_URL = "http://test_ultimate-sitemap-parser.com"  # mocked by HTTPretty

    # Publication / "last modified" date
    TEST_DATE_DATETIME = datetime.datetime(
        year=2009,
        month=12,
        day=17,
        hour=12,
        minute=4,
        second=56,
        tzinfo=tzoffset(None, 7200),
    )
    TEST_DATE_STR_RFC2822 = format_datetime(TEST_DATE_DATETIME)
    """Test string date formatted as RFC 2822 (for RSS 2.0 sitemaps)."""
    TEST_DATE_STR_ISO8601 = TEST_DATE_DATETIME.isoformat()
    """Test string date formatted as ISO 8601 (for XML and Atom 0.3 / 1.0 sitemaps)."""

    TEST_PUBLICATION_LANGUAGE = "en"
    TEST_PUBLICATION_NAME = "Test publication"

    @staticmethod
    def fallback_to_404_not_found_matcher(request):
        """Reply with "404 Not Found" to unmatched URLs instead of throwing NoMockAddress."""
        return rq_mock.create_response(
            request,
            status_code=404,
            reason="Not Found",
            headers={"Content-Type": "text/html"},
            text="<h1>404 Not Found!</h1>",
        )
