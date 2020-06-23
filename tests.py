import unittest
from logging import getLogger
from multiprocessing import Process
from time import sleep

import requests

import redirector

logger = getLogger('redirector.tests')


class TestRedirector(unittest.TestCase):
    RUNNING_APP = None
    SCHEMA = 'http'
    HOST = 'localhost'
    PORT = '8080'

    # Setup server

    @classmethod
    def setUpClass(cls) -> None:
        # server_options = {'host': cls.HOST, 'port': cls.PORT,
        #                   'reloader': True, 'debug': True,
        #                   'quiet': True}
        # from tests_server import run_server
        # cls.RUNNING_APP = Process(target=run_server, daemon=True,
        #                           kwargs=server_options)
        # cls.RUNNING_APP.start()

        status_code, cnt, interval = None, 10, 0.1
        logger.info(f'Waiting {cnt * interval}sec to start a server...')

        while status_code != 200 and cnt:
            try:
                status_code = requests.get(cls._get_url('status')).status_code
            except requests.RequestException:
                cnt -= 1
            sleep(0.1)

        logger.info('Started.' if cnt else 'Failed to start server.')

    # @classmethod
    # def tearDownClass(cls) -> None:
    #     cls.RUNNING_APP.terminate()
    #     status_code = 200
    #     while status_code == 200:
    #         try:
    #             status_code = requests.get(cls._get_url('status')).status_code
    #         except requests.RequestException:
    #             break
    #         sleep(0.1)

    def setUp(self) -> None:
        self.assertTrue(requests.get(self._get_url('status')).status_code == 200)

    # Helper functions

    @classmethod
    def _get_url(cls, uri: str = '') -> str:
        return f'{cls.SCHEMA}://{cls.HOST}:{cls.PORT}/{uri}'

    def _get_redirects_url(self, num_of_redirects: int) -> str:
        if num_of_redirects < 0:
            # limitless
            return self._get_url('redirect/limitless')
        # 0 for non-redirects
        return self._get_url(f'redirect/limited/{num_of_redirects}')

    # Redirect tests

    def test_no_redirects(self):
        correct_url = self._get_redirects_url(0)

        self.assertEqual(redirector.resolve_redirects(correct_url), correct_url)

    def test_positive_redirects(self):
        redirects_limit = 10
        start_url = self._get_redirects_url(redirector.RD_MAX_REDIRECTS)
        correct_url = self._get_redirects_url(0)

        self.assertEqual(
            redirector.resolve_redirects(start_url, max_redirects=redirects_limit),
            correct_url
        )

    def test_cycle_redirects(self):
        start_url = self._get_redirects_url(-1)

        with self.assertRaises(redirector.RDCycleRedirectsException):
            redirector.resolve_redirects(start_url)

    def test_too_many_redirects(self):
        start_url = self._get_redirects_url(redirector.RD_MAX_REDIRECTS + 1)

        with self.assertRaises(redirector.RDTooManyRedirectsException):
            redirector.resolve_redirects(start_url)

    # Body size tests

    def test_big_body(self):
        content_limit = 1000
        url = self._get_url('limitless_body')

        with self.assertRaises(redirector.RDTooBigBodyException):
            redirector.resolve_redirects(url, content_limit=content_limit)

    def test_big_body_redirect(self):
        url = self._get_url('redirect/4k_body')

        # should raise redirects error, ignore body size
        with self.assertRaises(redirector.RDCycleRedirectsException):
            redirector.resolve_redirects(url, 10, 100)

        with self.assertRaises(redirector.RDCycleRedirectsException):
            redirector.resolve_redirects(url, 10, 10000)


if __name__ == '__main__':
    unittest.main()
