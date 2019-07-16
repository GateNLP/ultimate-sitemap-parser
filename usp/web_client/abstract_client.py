"""Abstract web client class."""

import abc
from typing import Optional


class AbstractWebClientResponse(object, metaclass=abc.ABCMeta):
    """Abstract web client response."""

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
        """Return undecoded raw data of the response."""
        raise NotImplementedError("Abstract method.")

    def is_success(self) -> bool:
        """Return True if the request succeeded."""
        return 200 <= self.status_code() < 300

    def encountered_client_error(self) -> bool:
        """Return True if encountered HTTP client error."""
        return 400 <= self.status_code() < 500


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
