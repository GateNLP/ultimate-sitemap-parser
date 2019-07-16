import datetime

import pytest

from usp.exceptions import StripURLToHomepageException
from usp.helpers import html_unescape_strip, parse_sitemap_publication_date, is_http_url, strip_url_to_homepage


def test_html_unescape_strip():
    assert html_unescape_strip("  tests &amp; tests  ") == "tests & tests"
    assert html_unescape_strip(None) is None


def test_parse_sitemap_publication_date():
    assert parse_sitemap_publication_date("1997-07-16") == datetime.datetime(year=1997, month=7, day=16)
    assert parse_sitemap_publication_date("1997-07-16T19:20+01:00") == datetime.datetime(
        year=1997, month=7, day=16, hour=19, minute=20,
        tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)),
    )
    assert parse_sitemap_publication_date("1997-07-16T19:20:30+01:00") == datetime.datetime(
        year=1997, month=7, day=16, hour=19, minute=20, second=30,
        tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)),
    )
    assert parse_sitemap_publication_date("1997-07-16T19:20:30.45+01:00") == datetime.datetime(
        year=1997, month=7, day=16, hour=19, minute=20, second=30, microsecond=450000,
        tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)),
    )

    # "Z" timezone instead of "+\d\d:\d\d"
    assert parse_sitemap_publication_date("2018-01-12T21:57:27Z") == datetime.datetime(
        year=2018, month=1, day=12, hour=21, minute=57, second=27, tzinfo=datetime.timezone.utc,
    )


# noinspection SpellCheckingInspection
def test_is_http_url():
    # noinspection PyTypeChecker
    assert not is_http_url(None)
    assert not is_http_url('')

    assert not is_http_url('abc')
    assert not is_http_url('/abc')
    assert not is_http_url('//abc')
    assert not is_http_url('///abc')

    assert not is_http_url('gopher://gopher.floodgap.com/0/v2/vstat')
    assert not is_http_url('ftp://ftp.freebsd.org/pub/FreeBSD/')

    assert is_http_url('http://cyber.law.harvard.edu/about')
    assert is_http_url('https://github.com/berkmancenter/mediacloud')

    # URLs with port, HTTP auth, localhost
    assert is_http_url('https://username:password@domain.com:12345/path?query=string#fragment')
    assert is_http_url('http://localhost:9998/feed')
    assert is_http_url('http://127.0.0.1:12345/456789')
    assert is_http_url('http://127.0.00000000.1:8899/tweet_url?id=47')

    # Travis URL
    assert is_http_url('http://testing-gce-286b4005-b1ae-4b1a-a0d8-faf85e39ca92:37873/gv/tests.rss')

    # URLs with mistakes fixable by fix_common_url_mistakes()
    assert not is_http_url(
        'http:/www.theinquirer.net/inquirer/news/2322928/net-neutrality-rules-lie-in-tatters-as-fcc-overruled'
    )

    # UTF-8 in paths
    assert is_http_url('http://www.example.com/šiaurė.html')

    # IDN
    assert is_http_url('http://www.šiaurė.lt/šiaurė.html')
    assert is_http_url('http://www.xn--iaur-yva35b.lt/šiaurė.html')
    assert is_http_url('http://.xn--iaur-yva35b.lt') is False  # Invalid Punycode


def test_strip_url_to_homepage():
    assert strip_url_to_homepage('http://www.cwi.nl:80/%7Eguido/Python.html') == 'http://www.cwi.nl:80/'

    # HTTP auth
    assert strip_url_to_homepage(
        'http://username:password@www.cwi.nl/page.html'
    ) == 'http://username:password@www.cwi.nl/'

    # UTF-8 in paths
    assert strip_url_to_homepage('http://www.example.com/šiaurė.html') == 'http://www.example.com/'

    # IDN
    assert strip_url_to_homepage('https://www.šiaurė.lt/šiaurė.html') == 'https://www.šiaurė.lt/'
    assert strip_url_to_homepage('http://www.xn--iaur-yva35b.lt/šiaurė.html') == 'http://www.xn--iaur-yva35b.lt/'

    with pytest.raises(StripURLToHomepageException):
        # noinspection PyTypeChecker
        strip_url_to_homepage(None)

    with pytest.raises(StripURLToHomepageException):
        strip_url_to_homepage('')

    with pytest.raises(StripURLToHomepageException):
        strip_url_to_homepage('not an URL')
