import logging
import re
import socket
from http import HTTPStatus

import pytest

from usp import __version__
from usp.web_client.abstract_client import (
    AbstractWebClientSuccessResponse,
    WebClientErrorResponse,
)
from usp.web_client.requests_client import RequestsWebClient


class TestRequestsClient:
    TEST_BASE_URL = "http://test-ultimate-sitemap-parser.com"  # mocked by HTTPretty
    TEST_CONTENT_TYPE = "text/html"

    @pytest.fixture
    def client(self):
        return RequestsWebClient()

    def test_get(self, client, requests_mock):
        test_url = self.TEST_BASE_URL + "/"
        test_content = "This is a homepage."

        requests_mock.get(
            test_url,
            headers={"Content-Type": self.TEST_CONTENT_TYPE},
            text=test_content,
        )

        response = client.get(test_url)

        assert response
        assert isinstance(response, AbstractWebClientSuccessResponse)
        assert response.status_code() == HTTPStatus.OK.value
        assert response.status_message() == HTTPStatus.OK.phrase
        assert response.header("Content-Type") == self.TEST_CONTENT_TYPE
        assert response.header("content-type") == self.TEST_CONTENT_TYPE
        assert response.header("nonexistent") is None
        assert response.raw_data().decode("utf-8") == test_content

    def test_get_user_agent(self, client, requests_mock):
        test_url = self.TEST_BASE_URL + "/"

        def content_user_agent(request, context):
            context.status_code = HTTPStatus.OK.value
            return request.headers.get("User-Agent", "unknown")

        requests_mock.get(
            test_url,
            text=content_user_agent,
        )

        response = client.get(test_url)

        assert response
        assert isinstance(response, AbstractWebClientSuccessResponse)

        content = response.raw_data().decode("utf-8")
        assert content == f"ultimate_sitemap_parser/{__version__}"

    def test_get_not_found(self, client, requests_mock):
        test_url = self.TEST_BASE_URL + "/404.html"

        requests_mock.get(
            test_url,
            status_code=HTTPStatus.NOT_FOUND.value,
            reason=HTTPStatus.NOT_FOUND.phrase,
            headers={"Content-Type": self.TEST_CONTENT_TYPE},
            text="This page does not exist.",
        )

        response = client.get(test_url)

        assert response
        assert isinstance(response, WebClientErrorResponse)
        assert response.retryable() is False

    def test_get_nonexistent_domain(self, client):
        test_url = "http://www.totallydoesnotexisthjkfsdhkfsd.com/some_page.html"

        response = client.get(test_url)

        assert response
        assert isinstance(response, WebClientErrorResponse)
        assert response.retryable() is False
        assert (
            re.search(
                r"Failed to (establish a new connection|resolve)", response.message()
            )
            is not None
        )

    def test_get_timeout(self, client):
        sock = socket.socket()
        sock.bind(("", 0))
        socket_port = sock.getsockname()[1]
        assert socket_port
        sock.listen(1)

        test_timeout = 1
        test_url = f"http://127.0.0.1:{socket_port}/slow_page.html"

        client.set_timeout(test_timeout)

        response = client.get(test_url)

        sock.close()

        assert response
        assert isinstance(response, WebClientErrorResponse)
        assert response.retryable() is True
        assert "Read timed out" in response.message()

    def test_get_max_response_data_length(self, client, requests_mock):
        actual_length = 1024 * 1024
        max_length = 1024 * 512

        test_url = self.TEST_BASE_URL + "/huge_page.html"
        test_content = "a" * actual_length

        requests_mock.get(
            test_url,
            headers={"Content-Type": self.TEST_CONTENT_TYPE},
            text=test_content,
        )

        client.set_max_response_data_length(max_length)

        response = client.get(test_url)

        assert response
        assert isinstance(response, AbstractWebClientSuccessResponse)

        response_length = len(response.raw_data())
        assert response_length == max_length

    def test_error_page_log(self, client, requests_mock, caplog):
        caplog.set_level(logging.INFO)
        test_url = self.TEST_BASE_URL + "/error_page.html"

        requests_mock.get(
            test_url,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            text="This page is broken.",
        )

        client.get(test_url)

        assert "Response content: This page is broken." in caplog.text
