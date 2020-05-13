from django.core.cache import caches

from .settings import CACHE_HELPERS_ALIAS, CACHE_HELPERS_KEY_PREFIX, CACHE_HELPERS_KEY


def set_cache_bust_status(bust_key=None):
    cache = caches[CACHE_HELPERS_ALIAS]
    cache.set('{}.{}'.format(CACHE_HELPERS_KEY_PREFIX, CACHE_HELPERS_KEY), bust_key)


def get_bust_key():
    cache = caches[CACHE_HELPERS_ALIAS]
    return cache.get('{}.{}'.format(CACHE_HELPERS_KEY_PREFIX, CACHE_HELPERS_KEY), None)


def mark_response_as_processed(response):
    setattr(response, '_already_cahed', True)


def check_response_has_been_processed(response):
    return getattr(response, '_already_cahed', False)


def check_bust_header(request):
    bust_key = request.META.get('HTTP_BUST', '')
    return False if (not bust_key or bust_key != get_bust_key()) else True
