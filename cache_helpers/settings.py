from django.conf import settings


CACHE_HELPERS_ALIAS = getattr(settings, 'CACHE_HELPERS_ALIAS', settings.CACHE_MIDDLEWARE_ALIAS)
CACHE_HELPERS_KEY = getattr(settings, 'CACHE_HELPERS_KEY', 'cache_helpers_key')
