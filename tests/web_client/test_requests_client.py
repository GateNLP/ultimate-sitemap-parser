import socket
from http import HTTPStatus
from unittest import TestCase

import requests_mock

from usp.__about__ import __version__
from usp.web_client.abstract_client import (
    AbstractWebClientSuccessResponse,
    WebClientErrorResponse,
)
from usp.web_client.requests_client import RequestsWebClient


class TestRequestsClient(TestCase):
    TEST_BASE_URL = 'http://test_ultimate_sitemap_parser.com'  # mocked by HTTPretty
    TEST_CONTENT_TYPE = 'text/html'

    __slots__ = [
        '__client',
    ]

    def setUp(self) -> None:
        super().setUp()

        self.__client = RequestsWebClient()

    def test_get(self):
        with requests_mock.Mocker() as m:
            test_url = self.TEST_BASE_URL + '/'
            test_content = 'This is a homepage.'

            m.get(
                test_url,
                headers={'Content-Type': self.TEST_CONTENT_TYPE},
                text=test_content,
            )

            response = self.__client.get(test_url)

            assert response
            assert isinstance(response, AbstractWebClientSuccessResponse)
            assert response.status_code() == HTTPStatus.OK.value
            assert response.status_message() == HTTPStatus.OK.phrase
            assert response.header('Content-Type') == self.TEST_CONTENT_TYPE
            assert response.header('content-type') == self.TEST_CONTENT_TYPE
            assert response.header('nonexistent') is None
            assert response.raw_data().decode('utf-8') == test_content

    def test_get_user_agent(self):
        with requests_mock.Mocker() as m:
            test_url = self.TEST_BASE_URL + '/'

            def content_user_agent(request, context):
                context.status_code = HTTPStatus.OK.value
                return request.headers.get('User-Agent', 'unknown')

            m.get(
                test_url,
                text=content_user_agent,
            )

            response = self.__client.get(test_url)

            assert response
            assert isinstance(response, AbstractWebClientSuccessResponse)

            content = response.raw_data().decode('utf-8')
            assert content == 'ultimate_sitemap_parser/{}'.format(__version__)

    def test_get_not_found(self):
        with requests_mock.Mocker() as m:
            test_url = self.TEST_BASE_URL + '/404.html'

            m.get(
                test_url,
                status_code=HTTPStatus.NOT_FOUND.value,
                reason=HTTPStatus.NOT_FOUND.phrase,
                headers={'Content-Type': self.TEST_CONTENT_TYPE},
                text='This page does not exist.',
            )

            response = self.__client.get(test_url)

            assert response
            assert isinstance(response, WebClientErrorResponse)
            assert response.retryable() is False

    def test_get_nonexistent_domain(self):
        test_url = 'http://www.totallydoesnotexisthjkfsdhkfsd.com/some_page.html'

        response = self.__client.get(test_url)

        assert response
        assert isinstance(response, WebClientErrorResponse)
        assert response.retryable() is False
        assert 'Failed to establish a new connection' in response.message()

    def test_get_timeout(self):
        sock = socket.socket()
        sock.bind(('', 0))
        socket_port = sock.getsockname()[1]
        assert socket_port
        sock.listen(1)

        test_timeout = 1
        test_url = 'http://127.0.0.1:{}/slow_page.html'.format(socket_port)

        self.__client.set_timeout(test_timeout)

        response = self.__client.get(test_url)

        sock.close()

        assert response
        assert isinstance(response, WebClientErrorResponse)
        assert response.retryable() is True
        assert 'Read timed out' in response.message()

    def test_get_max_response_data_length(self):
        with requests_mock.Mocker() as m:
            actual_length = 1024 * 1024
            max_length = 1024 * 512

            test_url = self.TEST_BASE_URL + '/huge_page.html'
            test_content = 'a' * actual_length

            m.get(
                test_url,
                headers={'Content-Type': self.TEST_CONTENT_TYPE},
                text=test_content,
            )

            self.__client.set_max_response_data_length(max_length)

            response = self.__client.get(test_url)

            assert response
            assert isinstance(response, AbstractWebClientSuccessResponse)

            response_length = len(response.raw_data())
            assert response_length == max_length
