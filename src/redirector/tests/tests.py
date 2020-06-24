import unittest
from logging import getLogger
from time import sleep

import requests

from src import redirector
from src.redirector import Redirector

logger = getLogger('redirector.tests')


class TestRedirector(unittest.TestCase):
    RUNNING_APP = None
    SCHEMA = 'http'
    HOST = 'localhost'
    PORT = '8080'

    # Redirect tests
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.correct_url = self._get_redirects_url(0)

    def test_no_redirects(self):
        self.assertEqual(
            Redirector().resolve_redirects(self.correct_url),
            self.correct_url
        )

    def test_positive_redirects(self):
        redirects_limit = 10
        start_url = self._get_redirects_url(redirects_limit)

        self.assertEqual(
            Redirector(max_redirects=redirects_limit).resolve_redirects(start_url),
            self.correct_url
        )

    def test_cycle_redirects(self):
        start_url = self._get_redirects_url(-1)

        with self.assertRaises(redirector.RDCycleRedirectsException):
            Redirector().resolve_redirects(start_url)

    def test_too_many_redirects(self):
        redirects_limit = 10
        start_url = self._get_redirects_url(redirects_limit + 1)

        with self.assertRaises(redirector.RDTooManyRedirectsException):
            Redirector(max_redirects=redirects_limit).resolve_redirects(start_url)

    # Body size tests

    def test_big_body(self):
        content_limit = 1000
        url = self._get_url('limitless_body')

        with self.assertRaises(redirector.RDTooBigBodyException):
            Redirector(content_limit=content_limit).resolve_redirects(url)

    def test_big_body_redirect(self):
        url = self._get_url('redirect/4k_body')

        # should raise redirects error, ignore body size
        with self.assertRaises(redirector.RDCycleRedirectsException):
            Redirector(10, 100).resolve_redirects(url)

        with self.assertRaises(redirector.RDCycleRedirectsException):
            Redirector(10, 10000).resolve_redirects(url)

    # Setup server

    @classmethod
    def setUpClass(cls) -> None:
        status_code, cnt, interval = None, 10, 0.1
        logger.info(f'Waiting {cnt * interval}sec to start a server...')

        while status_code != 200 and cnt:
            try:
                status_code = requests.get(cls._get_url('status')).status_code
            except requests.RequestException:
                cnt -= 1
            sleep(0.1)

        logger.info('Started.' if cnt else 'Failed to start server.')

    def setUp(self) -> None:
        # check server is running
        self.assertTrue(requests.get(self._get_url('status')).status_code == 200)

    # Helper functions

    @classmethod
    def _get_url(cls, uri: str = '') -> str:
        return f'{cls.SCHEMA}://{cls.HOST}:{cls.PORT}/{uri}'

    def _get_redirects_url(self, num_of_redirects: int) -> str:
        if num_of_redirects < 0:
            # limitless
            return self._get_url('redirect/limitless')
        return self._get_url(f'redirect/limited/{num_of_redirects}')


if __name__ == '__main__':
    unittest.main()
