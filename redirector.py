import requests
from logging import getLogger

from exceptions import (
    RDCycleRedirectsException,
    RDTooBigBodyException,
    RDTooManyRedirectsException
)


logger = getLogger('redirector_proj')


RD_MAX_REDIRECTS = 30
RD_CONTENT_LIMIT = 4 * 8 * 2 ** 30   # 4 MB


def resolve_redirects(link, max_redirects=RD_MAX_REDIRECTS, content_limit=RD_CONTENT_LIMIT):
    logger.debug('Starting from `%s`', link)
    curr_link = link
    last_is_redirect = True
    visited_pages = set()
    redirects = 0

    while last_is_redirect:
        if curr_link in visited_pages:
            raise RDCycleRedirectsException('Cycle redirects found: `%s`' % visited_pages)

        visited_pages.add(curr_link)

        with requests.get(curr_link, stream=True, allow_redirects=False) as r:
            curr_link = r.headers.get('location', None) or curr_link
            last_is_redirect = r.is_redirect

            if last_is_redirect:
                redirects += 1
                logger.debug('Redirected to `%s` (%d/%d)',
                             curr_link, redirects, max_redirects)
                if redirects > RD_MAX_REDIRECTS:
                    raise RDTooManyRedirectsException(
                        'Too many redirects: `%s`, `%s`.' %
                        (visited_pages, max_redirects))
            else:
                content_length = r.headers.get('content-length', 0)
                body = b''

                if not content_length:   # content length is not defined, read by chunks
                    for chunk in r.iter_content(content_limit + 1):
                        body += chunk
                        break
                else:
                    body = r.text[:content_limit + 1]

                if len(body) > content_limit:
                    logger.info('Starting content (limited to `%s`): `%s`...', content_limit, body)
                    raise RDTooBigBodyException('Body size is too big.')

    return curr_link


if __name__ == '__main__':
    base = 'http://localhost:8080/'
    res = resolve_redirects(f'{base}redirect/limitless_body', 10, 100)
    print(res)