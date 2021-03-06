import requests
import uuid

from django.conf import settings

from ..utils import set_cache_bust_status
from ..settings import logger

from .helpers import BaseRequestMixin, BaseRequestCommand


def get_session(basic_auth=None, login=None):
    session = requests.session()

    kwargs = {}

    if basic_auth:
        kwargs['auth'] = (basic_auth['username'], basic_auth['password'])

    if login is not None:
        session.headers.update({'referer': login.get('referer')})
        res = session.get(login['url'], **kwargs)
        res = session.post(login['url'], allow_redirects=True, data={
            'username': login['username'],
            'password': login['password'],
            'csrfmiddlewaretoken': res.cookies['csrftoken'],
            'next': login['url'],
        }, **kwargs)

        # success has history of redirections
        if not len(res.history):
            raise Exception('Login failed')
        else:
            logger.info('Login success')

    return session


def _make_request(url, session=None, bust_key=None, basic_auth=None, login=None, lang=None):
    session = session if session is not None else get_session(basic_auth=basic_auth, login=login)

    kwargs = {
        'cookies': {},
        'headers': {},
    }

    if lang:
        kwargs['cookies'][settings.LANGUAGE_COOKIE_NAME] = lang

    try:
        kwargs['headers']['bust'] = bust_key if bust_key is not None else ''

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
    session = get_session(basic_auth=basic_auth, login=login)
    try:
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

    def _make_requests(self, threads=1, **extra):
        session = get_session(
                basic_auth=self.get_request_basic_auth(),
                login=extra.get('login', None))
        try:
            bust_key = str(uuid.uuid4())
            set_cache_bust_status(bust_key)
            extra['bust_key'] = bust_key
            extra['session'] = session
            return super()._make_requests(threads=threads, **extra)
        finally:
            set_cache_bust_status()


class RealRequestCommand(RealRequestMixin, BaseRequestCommand):
    pass
