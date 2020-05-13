import time
from functools import wraps

from django.core.cache import caches
from django.utils.cache import add_never_cache_headers, patch_response_headers
from django.utils.http import http_date

from .utils import check_bust_header
from .settings import CACHE_HELPERS_ALIAS, CACHE_HELPERS_KEY_PREFIX


def _cache_page(timeout, key_func, cache_alias=None, key_prefix=None, check_func=None, patch_func=None):
    def _cache(view_func):
        @wraps(view_func)
        def __cache(request, *args, **kwargs):
            _cache_alias = cache_alias if cache_alias is not None else CACHE_HELPERS_ALIAS
            _key_prefix = key_prefix if key_prefix is not None else CACHE_HELPERS_KEY_PREFIX
            cache = caches[_cache_alias]
            cache_key = key_func(request, _key_prefix, cache)
            response = cache.get(cache_key)
            if not response or (check_func is not None and check_func(request)):
                response = view_func(request, *args, **kwargs)
                if response.status_code == 200:
                    patch_func(response, timeout)
                    if hasattr(response, 'render') and callable(response.render):
                        response.add_post_render_callback(
                            lambda r: cache.set(cache_key, r, timeout)
                        )
                    else:
                        cache.set(cache_key, response, timeout)
            setattr(request, '_cache_update_cache', False)
            return response
        return __cache
    return _cache


def cache_page(timeout, key_func, cache=None, key_prefix=None):
    return _cache_page(
        timeout,
        key_func,
        cache_alias=cache,
        key_prefix=key_prefix,
        patch_func=patch_response_headers)


def cache_page_forever(timeout, key_func, cache=None, key_prefix=None):
    def patch_expires_header(response, *args):
        if timeout is None or timeout == 0 or timeout < 0:
            add_never_cache_headers(response)
        else:
            response['Expires'] = http_date(time.time() + timeout)
    return _cache_page(
        None,
        key_func,
        cache_alias=cache,
        key_prefix=key_prefix,
        check_func=check_bust_header,
        patch_func=patch_expires_header)