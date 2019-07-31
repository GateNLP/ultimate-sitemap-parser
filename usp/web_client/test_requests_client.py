from http import HTTPStatus
from unittest import TestCase

import requests_mock

from usp.__about__ import __version__

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
            assert response.is_success() is True
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
            assert response.is_success() is True

            content = response.raw_data().decode('utf-8')
            assert content == 'ultimate_sitemap_parser/{}'.format(__version__)

    def test_get_not_found(self):
        with requests_mock.Mocker() as m:
            test_url = self.TEST_BASE_URL + '/404.html'
            test_content = 'This page does not exist.'

            m.get(
                test_url,
                status_code=HTTPStatus.NOT_FOUND.value,
                reason=HTTPStatus.NOT_FOUND.phrase,
                headers={'Content-Type': self.TEST_CONTENT_TYPE},
                text=test_content,
            )

            response = self.__client.get(test_url)

            assert response
            assert response.is_success() is False
            assert response.status_code() == HTTPStatus.NOT_FOUND.value
            assert response.status_message() == HTTPStatus.NOT_FOUND.phrase
            assert response.raw_data().decode('utf-8') == test_content

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
            assert response.is_success() is True

            response_length = len(response.raw_data())
            assert response_length == max_length
