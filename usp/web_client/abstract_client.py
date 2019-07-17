"""Abstract web client class."""

import abc
from http import HTTPStatus
from typing import Optional


class AbstractWebClientResponse(object, metaclass=abc.ABCMeta):
    """Abstract web client response."""

    _RETRYABLE_HTTP_STATUS_CODES = {

        # Some servers return "400 Bad Request" initially but upon retry start working again, no idea why
        HTTPStatus.BAD_REQUEST.value,

        # If we timed out requesting stuff, we can just try again
        HTTPStatus.REQUEST_TIMEOUT.value,

        # If we got rate limited, it makes sense to wait a bit
        HTTPStatus.TOO_MANY_REQUESTS.value,

        # Server might be just fine on a subsequent attempt
        HTTPStatus.INTERNAL_SERVER_ERROR.value,

        # Upstream might reappear on a retry
        HTTPStatus.BAD_GATEWAY.value,

        # Service might become available again on a retry
        HTTPStatus.SERVICE_UNAVAILABLE.value,

        # Upstream might reappear on a retry
        HTTPStatus.GATEWAY_TIMEOUT.value,

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

    @abc.abstractmethod
    def status_code(self) -> int:
        """Return HTTP status code of the response."""
        raise NotImplementedError("Abstract method.")

    @abc.abstractmethod
    def status_message(self) -> str:
        """Return HTTP status message of the response."""
        raise NotImplementedError("Abstract method.")

    @abc.abstractmethod
    def header(self, case_insensitive_name: str) -> Optional[str]:
        """Return HTTP header value for a given case-insensitive name, or None if such header wasn't set."""
        raise NotImplementedError("Abstract method.")

    @abc.abstractmethod
    def raw_data(self) -> bytes:
        """Return encoded raw data of the response."""
        raise NotImplementedError("Abstract method.")

    def is_success(self) -> bool:
        """Return True if the request succeeded."""
        return 200 <= self.status_code() < 300

    def is_retryable_error(self) -> bool:
        """Return True if encountered HTTP error which should be retried."""
        return self.status_code() in self._RETRYABLE_HTTP_STATUS_CODES


class AbstractWebClient(object, metaclass=abc.ABCMeta):
    """Abstract web client to be used by the sitemap fetcher."""

    @abc.abstractmethod
    def set_max_response_data_length(self, max_response_data_length: int):
        """Initialize web client with max. response length in bytes."""
        raise NotImplementedError("Abstract method.")

    @abc.abstractmethod
    def get(self, url: str) -> AbstractWebClientResponse:
        """GET an URL and return a response."""
        raise NotImplementedError("Abstract method.")
