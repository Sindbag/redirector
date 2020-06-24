#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Redirector is an easy to use safe redirects follower.
Copyright (c) 2020, Anatoly Bardukov.
License: MIT (see LICENSE for details)
"""

import requests
from logging import getLogger

from .exceptions import (
    RDCycleRedirectsException,
    RDTooBigBodyException,
    RDTooManyRedirectsException
)


__author__ = 'Anatoly Bardukov'
__version__ = '0.0.1-dev'
__license__ = 'MIT'


logger = getLogger('redirector')


class Redirector:
    RD_MAX_REDIRECTS = 30
    RD_CONTENT_LIMIT = 4 * 8 * 2 ** 30  # 4 MB

    def __init__(self, max_redirects=RD_MAX_REDIRECTS,
                 content_limit=RD_CONTENT_LIMIT):
        self.max_redirects = max_redirects
        self.content_limit = content_limit

        # internal state
        self._curr_link = None
        self._last_is_redirect = True
        self._visited_pages = set()

    def resolve_redirects(self, link: str) -> str:
        logger.debug('Starting from `%s`', link)
        # set state
        self._curr_link = link
        self._last_is_redirect = True
        self._visited_pages = set()

        while self._last_is_redirect:  # possible to use Session
            if self._curr_link in self._visited_pages:
                raise RDCycleRedirectsException(
                        'Cycle redirects found: `%s`' %
                        self._visited_pages)

            self._visited_pages.add(self._curr_link)

            with requests.get(self._curr_link, stream=True,
                              allow_redirects=False) as r:
                self._process_response(r)

        logger.debug('Visited pages: `%s`', self._visited_pages)
        return self._curr_link

    def _process_response(self, response):
        self._curr_link = response.headers.get('location', None) \
                          or self._curr_link
        self._last_is_redirect = response.is_redirect

        if self._last_is_redirect:
            self._process_redirect()
        else:
            self._process_body(response)

    def _process_redirect(self):
        logger.debug('Redirected to `%s` (%d/%d)',
                     self._curr_link, len(self._visited_pages),
                     self.max_redirects)
        if len(self._visited_pages) > self.max_redirects:
            raise RDTooManyRedirectsException(
                      'Too many redirects: `%s`, `%s`.' %
                      (self._visited_pages, self.max_redirects))

    def _process_body(self, response):
        content_length = response.headers.get('content-length', 0)
        body = b''

        if not content_length:  # content length is not defined, read by chunks
            for chunk in response.iter_content(self.content_limit + 1):
                body += chunk
                break   # 1 iteration
        else:
            body = response.text[:self.content_limit + 1]

        if len(body) > self.content_limit:
            logger.debug('Content (limited to `%s`): `%s`...',
                         self.content_limit, body)
            raise RDTooBigBodyException('Body size is too big.')


if __name__ == '__main__':
    base = 'http://localhost:8080/'
    res = Redirector(10, 100).resolve_redirects(f'{base}redirect/limitless_body')
    print(res)