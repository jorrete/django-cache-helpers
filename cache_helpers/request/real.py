import logging
import requests
import uuid

from django.conf import settings

from ..utils import set_cache_bust_status

from .helpers import BaseRequestMixin, BaseRequestCommand


logger = logging.getLogger(__name__)


def get_session(basic_auth=None, login=None):
    session = requests.session()
    kwargs = {}

    if basic_auth:
        kwargs['auth'] = (basic_auth['username'], basic_auth['password'])

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

    return session


def _make_request(url, session, bust_key, basic_auth=None, login=None, lang=None):
    kwargs = {
        'cookies': {},
        'headers': {},
    }

    if lang:
        kwargs['cookies'][settings.LANGUAGE_COOKIE_NAME] = lang

    try:
        kwargs['headers']['bust'] = bust_key

        if basic_auth:
            kwargs['auth'] = (basic_auth['username'], basic_auth['password'])

        response = session.get(url, **kwargs)
        logger.info('Request success: {}{}{}'.format(
            url,
            ' [lang: {}]'.format(lang) if lang is not None else '',
            ' [username: {}]'.format(login['username']) if login is not None else ''))
    except Exception:
        logger.error('Request error: {}'.format(url))

    return response


def make_request(url, session=None, bust_key=None, basic_auth=None, login=None, lang=None):
    try:
        session = get_session(basic_auth=basic_auth, login=login)
        bust_key = str(uuid.uuid4())
        set_cache_bust_status(bust_key)
        return _make_request(
                url, session, bust_key,
                basic_auth=basic_auth, login=login, lang=lang)
    except Exception as e:
        raise e
    finally:
        set_cache_bust_status()


class RealRequestMixin(BaseRequestMixin):
    def get_request_runner(self):
        return _make_request

    def make_requests(self, threads=1, **extra):
        try:
            session = get_session(
                    basic_auth=self.get_request_basic_auth(),
                    login=self.get_request_login())
            bust_key = str(uuid.uuid4())
            set_cache_bust_status(bust_key)
            extra['bust_key'] = bust_key
            extra['session'] = session
            return super().make_requests(threads=threads, **extra)
        finally:
            set_cache_bust_status()


class RealRequestCommand(RealRequestMixin, BaseRequestCommand):
    pass
