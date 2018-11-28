"""requests-based implementation of web client class."""

from typing import Optional

import requests
from requests import Response

from .abstract_client import AbstractWebClientResponse, AbstractWebClient
from usp.__about__ import __version__


class RequestsWebClientResponse(AbstractWebClientResponse):
    """'requests' web client response."""

    __slots__ = [
        '__requests_response',
        '__max_response_data_length',
    ]

    def __init__(self, requests_response: Response, max_response_data_length: Optional[int]):
        self.__requests_response = requests_response
        self.__max_response_data_length = max_response_data_length

    def status_code(self) -> int:
        """Return HTTP status code of the response."""
        return int(self.__requests_response.status_code)

    def status_message(self) -> str:
        """Return HTTP status message of the response."""
        return self.__requests_response.reason

    def header(self, case_insensitive_name: str) -> Optional[str]:
        """Return HTTP header value for a given case-insensitive name, or None if such header wasn't set."""
        return self.__requests_response.headers.get(case_insensitive_name.lower(), None)

    def raw_data(self) -> bytes:
        """Return non-decoded raw binary data of the response."""
        if self.__max_response_data_length:
            data = self.__requests_response.content[:self.__max_response_data_length]
        else:
            data = self.__requests_response.content

        return data


class RequestsWebClient(AbstractWebClient):
    """'requests' web client to be used by the sitemap fetcher."""

    __USER_AGENT = 'ultimate_sitemap_parser/{}'.format(__version__)

    __HTTP_REQUEST_TIMEOUT = 60
    """HTTP request timeout.

    Some webservers might be generating huge sitemaps on the fly, so this is why it's rather big."""

    __slots__ = [
        '__max_response_data_length',
    ]

    def __init__(self):
        self.__max_response_data_length = None

    def set_max_response_data_length(self, max_response_data_length: int) -> None:
        self.__max_response_data_length = max_response_data_length

    def get(self, url: str) -> RequestsWebClientResponse:
        response = requests.get(
            url,
            timeout=self.__HTTP_REQUEST_TIMEOUT,
            stream=True,
            headers={'User-Agent': self.__USER_AGENT},
        )
        return RequestsWebClientResponse(
            requests_response=response,
            max_response_data_length=self.__max_response_data_length,
        )
