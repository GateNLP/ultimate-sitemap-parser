"""Abstract web client class."""

import abc
import random
import time
from http import HTTPStatus
from typing import Optional

RETRYABLE_HTTP_STATUS_CODES = {
    # Some servers return "400 Bad Request" initially but upon retry start working again, no idea why
    int(HTTPStatus.BAD_REQUEST),
    # If we timed out requesting stuff, we can just try again
    int(HTTPStatus.REQUEST_TIMEOUT),
    # If we got rate limited, it makes sense to wait a bit
    int(HTTPStatus.TOO_MANY_REQUESTS),
    # Server might be just fine on a subsequent attempt
    int(HTTPStatus.INTERNAL_SERVER_ERROR),
    # Upstream might reappear on a retry
    int(HTTPStatus.BAD_GATEWAY),
    # Service might become available again on a retry
    int(HTTPStatus.SERVICE_UNAVAILABLE),
    # Upstream might reappear on a retry
    int(HTTPStatus.GATEWAY_TIMEOUT),
    # (unofficial) 509 Bandwidth Limit Exceeded (Apache Web Server/cPanel)
    509,
    # (unofficial) 598 Network read timeout error
    598,
    # (unofficial, nginx) 499 Client Closed Request
    499,
    # (unofficial, Cloudflare) 520 Unknown Error
    520,
    # (unofficial, Cloudflare) 521 Web Server Is Down
    521,
    # (unofficial, Cloudflare) 522 Connection Timed Out
    522,
    # (unofficial, Cloudflare) 523 Origin Is Unreachable
    523,
    # (unofficial, Cloudflare) 524 A Timeout Occurred
    524,
    # (unofficial, Cloudflare) 525 SSL Handshake Failed
    525,
    # (unofficial, Cloudflare) 526 Invalid SSL Certificate
    526,
    # (unofficial, Cloudflare) 527 Railgun Error
    527,
    # (unofficial, Cloudflare) 530 Origin DNS Error
    530,
}
"""HTTP status codes on which a request should be retried."""


class AbstractWebClientResponse(metaclass=abc.ABCMeta):
    """
    Abstract response.
    """

    pass


class AbstractWebClientSuccessResponse(
    AbstractWebClientResponse, metaclass=abc.ABCMeta
):
    """
    Successful response.
    """

    @abc.abstractmethod
    def status_code(self) -> int:
        """
        Return HTTP status code of the response.

        :return: HTTP status code of the response, e.g. 200.
        """
        raise NotImplementedError("Abstract method.")

    @abc.abstractmethod
    def status_message(self) -> str:
        """
        Return HTTP status message of the response.

        :return: HTTP status message of the response, e.g. "OK".
        """
        raise NotImplementedError("Abstract method.")

    @abc.abstractmethod
    def header(self, case_insensitive_name: str) -> Optional[str]:
        """
        Return HTTP header value for a given case-insensitive name, or None if such header wasn't set.

        :param case_insensitive_name: HTTP header's name, e.g. "Content-Type".
        :return: HTTP header's value, or None if it was unset.
        """
        raise NotImplementedError("Abstract method.")

    @abc.abstractmethod
    def raw_data(self) -> bytes:
        """
        Return encoded raw data of the response.

        :return: Encoded raw data of the response.
        """
        raise NotImplementedError("Abstract method.")

    @abc.abstractmethod
    def url(self) -> str:
        """
        Return the actual URL fetched, after any redirects.

        :return: URL fetched.
        """
        raise NotImplementedError("Abstract method.")


class WebClientErrorResponse(AbstractWebClientResponse, metaclass=abc.ABCMeta):
    """
    Error response.
    """

    __slots__ = [
        "_message",
        "_retryable",
    ]

    def __init__(self, message: str, retryable: bool):
        """
        Constructor.

        :param message: Message describing what went wrong.
        :param retryable: True if the request should be retried.
        """
        super().__init__()
        self._message = message
        self._retryable = retryable

    def message(self) -> str:
        """
        Return message describing what went wrong.

        :return: Message describing what went wrong.
        """
        return self._message

    def retryable(self) -> bool:
        """
        Return True if request should be retried.

        :return: True if request should be retried.
        """
        return self._retryable


class AbstractWebClient(metaclass=abc.ABCMeta):
    """
    Abstract web client to be used by the sitemap fetcher.
    """

    @abc.abstractmethod
    def set_max_response_data_length(
        self, max_response_data_length: Optional[int]
    ) -> None:
        """
        Set the maximum number of bytes that the web client will fetch.

        :param max_response_data_length: Maximum number of bytes that the web client will fetch, or None to fetch all.
        """
        raise NotImplementedError("Abstract method.")

    @abc.abstractmethod
    def get(self, url: str) -> AbstractWebClientResponse:
        """
        Fetch a URL and return a response.

        Method shouldn't throw exceptions on connection errors (including timeouts); instead, such errors should be
        reported via Response object.

        :param url: URL to fetch.
        :return: Response object.
        """
        raise NotImplementedError("Abstract method.")


class NoWebClientException(Exception):
    """Error indicating this web client cannot fetch pages."""

    pass


class LocalWebClient(AbstractWebClient):
    """Dummy web client which is a valid implementation but errors if called.

    Used for local parsing
    """

    def set_max_response_data_length(
        self, max_response_data_length: Optional[int]
    ) -> None:
        pass

    def get(self, url: str) -> AbstractWebClientResponse:
        raise NoWebClientException


class LocalWebClientSuccessResponse(AbstractWebClientSuccessResponse):
    def __init__(self, url: str, data: str):
        self._url = url
        self._data = data

    def status_code(self) -> int:
        return 200

    def status_message(self) -> str:
        return "OK"

    def header(self, case_insensitive_name: str) -> Optional[str]:
        return None

    def raw_data(self) -> bytes:
        return self._data.encode("utf-8")

    def url(self) -> str:
        return self._url


class RequestWaiter:
    """
    Manages waiting between requests.
    """

    def __init__(self, wait: Optional[float] = None, random_wait: bool = True):
        """
        :param wait: time to wait between requests, in seconds.
        :param random_wait: if true, wait time is multiplied by a random number between 0.5 and 1.5.
        """
        self.wait_s = wait or 0
        self.random_wait = random_wait
        self.is_first = True

    def wait(self) -> None:
        """Perform a wait if needed. Should be called before each request.

        Will skip wait if this is the first request.
        """
        if self.wait_s == 0:
            return

        if self.is_first:
            self.is_first = False
            return

        wait_f = 1.0
        if self.random_wait:
            wait_f = random.uniform(0.5, 1.5)

        time.sleep(self.wait_s * wait_f)
