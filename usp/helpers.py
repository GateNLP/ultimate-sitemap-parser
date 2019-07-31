"""Helper utilities."""

import datetime
import gzip as gzip_lib
import html
import re
import time
from typing import Optional
from urllib.parse import urlparse, unquote_plus, urlunparse

from dateutil.parser import parse as dateutil_parse

from .exceptions import SitemapException, GunzipException, StripURLToHomepageException
from .log import create_logger
from .web_client.abstract_client import (
    AbstractWebClient,
    AbstractWebClientSuccessResponse,
    WebClientErrorResponse,
    AbstractWebClientResponse,
)

log = create_logger(__name__)

__URL_REGEX = re.compile(r'^https?://[^\s/$.?#].[^\s]*$', re.IGNORECASE)
"""Regular expression to match HTTP(s) URLs."""


def is_http_url(url: str) -> bool:
    """
    Returns true if URL is of the "http" ("https") scheme.

    :param url: URL to test.
    :return: True if argument URL is of the "http" ("https") scheme.
    """
    if url is None:
        log.debug("URL is None")
        return False
    if len(url) == 0:
        log.debug("URL is empty")
        return False

    log.debug("Testing if URL '{}' is HTTP(s) URL".format(url))

    if not re.search(__URL_REGEX, url):
        log.debug("URL '{}' does not match URL's regexp".format(url))
        return False

    try:
        # Try parsing the URL
        uri = urlparse(url)
        _ = urlunparse(uri)

    except Exception as ex:
        log.debug("Cannot parse URL {}: {}".format(url, ex))
        return False

    if not uri.scheme:
        log.debug("Scheme is undefined for URL {}.".format(url))
        return False
    if not uri.scheme.lower() in ['http', 'https']:
        log.debug("Scheme is not HTTP(s) for URL {}.".format(url))
        return False
    if not uri.hostname:
        log.debug("Host is undefined for URL {}.".format(url))
        return False

    return True


def html_unescape_strip(string: Optional[str]) -> Optional[str]:
    """
    Decode HTML entities, strip string, set to None if it's empty; ignore None as input.

    :param string: String to decode HTML entities in.
    :return: Stripped string with HTML entities decoded; None if parameter string was empty or None.
    """
    if string:
        string = html.unescape(string)
        string = string.strip()
        if not string:
            string = None
    return string


def parse_iso8601_date(date_string: str) -> datetime.datetime:
    """
    Parse ISO 8601 date (e.g. from sitemap's <publication_date>) into datetime.datetime object.

    :param date_string: ISO 8601 date, e.g. "2018-01-12T21:57:27Z" or "1997-07-16T19:20:30+01:00".
    :return: datetime.datetime object of a parsed date.
    """
    # FIXME parse known date formats faster

    if not date_string:
        raise SitemapException("Date string is unset.")

    date = dateutil_parse(date_string)

    return date


def parse_rfc2822_date(date_string: str) -> datetime.datetime:
    """
    Parse RFC 2822 date (e.g. from Atom's <issued>) into datetime.datetime object.

    :param date_string: RFC 2822 date, e.g. "Tue, 10 Aug 2010 20:43:53 -0000".
    :return: datetime.datetime object of a parsed date.
    """
    # FIXME parse known date formats faster
    return parse_iso8601_date(date_string)


def get_url_retry_on_client_errors(url: str,
                                   web_client: AbstractWebClient,
                                   retry_count: int = 5,
                                   sleep_between_retries: int = 1) -> AbstractWebClientResponse:
    """
    Fetch URL, retry on retryable errors.

    :param url: URL to fetch.
    :param web_client: Web client object to use for fetching.
    :param retry_count: How many times to retry fetching the same URL.
    :param sleep_between_retries: How long to sleep between retries, in seconds.
    :return: Web client response object.
    """
    assert retry_count > 0, "Retry count must be positive."

    response = None
    for retry in range(0, retry_count):
        log.info("Fetching URL {}...".format(url))
        response = web_client.get(url)

        if isinstance(response, WebClientErrorResponse):
            log.warning(
                "Request for URL {} failed: {}".format(
                    url, response.message()
                )
            )

            if response.retryable():
                log.info("Retrying URL {} in {} seconds...".format(url, sleep_between_retries))
                time.sleep(sleep_between_retries)

            else:
                log.info("Not retrying for URL {}".format(url))
                return response

        else:
            return response

    log.info("Giving up on URL {}".format(url))
    return response


def __response_is_gzipped_data(url: str, response: AbstractWebClientSuccessResponse) -> bool:
    """
    Return True if Response looks like it's gzipped.

    :param url: URL the response was fetched from.
    :param response: Response object.
    :return: True if response looks like it might contain gzipped data.
    """
    uri = urlparse(url)
    url_path = unquote_plus(uri.path)
    content_type = response.header('content-type') or ''

    if url_path.lower().endswith('.gz') or 'gzip' in content_type.lower():
        return True

    else:
        return False


def gunzip(data: bytes) -> bytes:
    """
    Gunzip data.

    :param data: Gzipped data.
    :return: Gunzipped data.
    """

    if data is None:
        raise GunzipException("Data is None.")

    if not isinstance(data, bytes):
        raise GunzipException("Data is not bytes: %s" % str(data))

    if len(data) == 0:
        raise GunzipException("Data is empty (no way an empty string is a valid Gzip archive).")

    try:
        gunzipped_data = gzip_lib.decompress(data)
    except Exception as ex:
        raise GunzipException("Unable to gunzip data: %s" % str(ex))

    if gunzipped_data is None:
        raise GunzipException("Gunzipped data is None.")

    if not isinstance(gunzipped_data, bytes):
        raise GunzipException("Gunzipped data is not bytes.")

    return gunzipped_data


def ungzipped_response_content(url: str, response: AbstractWebClientSuccessResponse) -> str:
    """
    Return HTTP response's decoded content, gunzip it if necessary.

    :param url: URL the response was fetched from.
    :param response: Response object.
    :return: Decoded and (if necessary) gunzipped response string.
    """

    data = response.raw_data()

    if __response_is_gzipped_data(url=url, response=response):
        try:
            data = gunzip(data)
        except GunzipException as ex:
            # In case of an error, just assume that it's one of the non-gzipped sitemaps with ".gz" extension
            log.error("Unable to gunzip response {}, maybe it's a non-gzipped sitemap: {}".format(response, ex))

    # FIXME other encodings
    data = data.decode('utf-8-sig', errors='replace')

    assert isinstance(data, str)

    return data


def strip_url_to_homepage(url: str) -> str:
    """
    Strip URL to its homepage.

    :param url: URL to strip, e.g. "http://www.example.com/page.html".
    :return: Stripped homepage URL, e.g. "http://www.example.com/"
    """
    if not url:
        raise StripURLToHomepageException("URL is empty.")

    try:
        uri = urlparse(url)
        assert uri.scheme, "Scheme must be set."
        assert uri.scheme.lower() in ['http', 'https'], "Scheme must be http:// or https://"
        uri = (
            uri.scheme,
            uri.netloc,
            '/',  # path
            '',  # params
            '',  # query
            '',  # fragment
        )
        url = urlunparse(uri)
    except Exception as ex:
        raise StripURLToHomepageException("Unable to parse URL {}: {}".format(url, ex))

    return url
