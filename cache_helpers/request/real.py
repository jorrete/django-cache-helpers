import logging
import requests
import uuid

from django.conf import settings

from ..utils import threaded_cue, set_cache_bust_status

from .helpers import BaseRequestMixin, BaseRequestCommand


logger = logging.getLogger(__name__)


def make_requests(threads=1, urls=[], basic_auth=None, login=None, lang=None):
    try:
        session = requests.session()
        bust_key = str(uuid.uuid4())
        set_cache_bust_status(bust_key)

        kwargs = {
            'cookies': {},
            'headers': {},
        }

        if lang is not None:
            kwargs['cookies'][settings.LANGUAGE_COOKIE_NAME] = lang

        def callback(url):
            try:
                kwargs['headers']['bust'] = bust_key

                if basic_auth:
                    kwargs['auth'] = (basic_auth['username'], basic_auth['password'])

                session.get(url, **kwargs)
                logger.info('Request success: {}{}{}'.format(
                    url,
                    ' [lang: {}]'.format(lang) if lang is not None else '',
                    ' [username: {}]'.format(login['username']) if login is not None else ''))
            except Exception as e:
                logger.error('Request error: {}'.format(url))
                raise e

        if login:
            req = session.get(login['url'], **kwargs)
            req = session.post(login['url'], data={
                'username': login['username'],
                'password': login['password'],
                'csrfmiddlewaretoken': req.cookies['csrftoken'],
                'next': login['url'],
            }, **kwargs)

            if req.status_code != 200:
                raise Exception('Login failed')
            else:
                logger.info('Login success')

        threaded_cue(urls, callback, threads)
    except Exception as e:
        raise e
    finally:
        set_cache_bust_status()


class RealRequestMixin(BaseRequestMixin):
    def get_request_runner(self):
        return make_requests


class RealRequestCommand(RealRequestMixin, BaseRequestCommand):
    pass
