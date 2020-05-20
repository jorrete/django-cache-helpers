from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.handlers.base import BaseHandler
from django.test import RequestFactory

from ..settings import logger

from .helpers import BaseRequestMixin, BaseRequestCommand


DUMMY_USERNAME = '__dummy_user__'


class CustomRequestFactory(RequestFactory):
    def generic(self, *args, **kwargs):
        if 'SERVER_PORT' in self.defaults:
            kwargs['SERVER_PORT'] = self.defaults['SERVER_PORT']
        if 'secure' in self.defaults:
            kwargs['secure'] = self.defaults['secure']
        return super().generic(*args, **kwargs)


def url_to_request(url_str, method='get', login=None, lang=None, **extra):
    url = urlparse(url_str)

    factory = CustomRequestFactory(
        secure=True if url.scheme == 'https' else False,
        SERVER_NAME=url.hostname,
        **{'SERVER_PORT': url.port} if url.port is not None else {})

    request = getattr(factory, method)(
            url_str.replace('{}://{}'.format(url.scheme, url.netloc), ''),
            **extra)

    # if i18n_patterns(*urls, prefix_default_language=True) will be ignored
    if lang is not None:
        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = lang
    if login is not None:
        User = get_user_model()
        user = (
            User if login.get('dummy', False) else
            User.objects.get)(username=login['username'])
        request._cached_user = user

    request._bust_cache = True
    return request


def make_request(url, login=None, lang=None, **kwargs):
    client = BaseHandler()
    client.load_middleware()

    if login is not None and not len(login['username']):
        login = {
            'dummy': True,
            'username': DUMMY_USERNAME,
        }

    request = url_to_request(url, login=login, lang=lang)
    response = client.get_response(request)

    if response.status_code == 200:
        logger.info('Request success: {}{}{}'.format(
            url,
            ' [lang: {}]'.format(lang) if lang is not None else '',
            ' [username: {}]'.format(login['username']) if login is not None else ''))
    else:
        logger.error('Request error: {}'.format(url))

    return response


class SyntheticRequestMixin(BaseRequestMixin):
    def get_request_runner(self):
        return make_request


class SyntheticRequestCommand(SyntheticRequestMixin, BaseRequestCommand):
    pass
