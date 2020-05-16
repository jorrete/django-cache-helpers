from .decorators import cache_page, cache_page_forever


class CachePageMixin(object):
    cache_key_prefix = None
    cache_cache = None

    def get_cache_timeout(self, request, *args, **kwargs):
        if not hasattr(self, 'cache_timeout'):
            raise ValueError('Missing cache_timeout attribute')
        return self.cache_timeout

    def cache_key_func(self, request, *args, **kwargs):
        raise NotImplementedError()

    def get_cache_cache(self, request, *args, **kwargs):
        return self.cache_cache

    def get_cache_key_prefix(self, request, *args, **kwargs):
        return self.cache_key_prefix

    def dispatch(self, request, *args, **kwargs):
        return cache_page(
            self.get_cache_timeout(request),
            self.cache_key_func,
            cache=self.get_cache_cache(request),
            key_prefix=self.get_cache_key_prefix()
        )(super().dispatch)(request, *args, **kwargs)


class CachePageForeverMixin(object):
    cache_key_prefix = None
    cache_cache = None

    def get_cache_timeout(self, request, *args, **kwargs):
        if not hasattr(self, 'cache_timeout'):
            raise ValueError('Missing cache_timeout attribute')
        return self.cache_timeout

    def cache_key_func(self, request, *args, **kwargs):
        raise NotImplementedError()

    def get_cache_cache(self, request, *args, **kwargs):
        return self.cache_cache

    def get_cache_key_prefix(self, request, *args, **kwargs):
        return self.cache_key_prefix

    def dispatch(self, request, *args, **kwargs):
        return cache_page_forever(
            self.get_cache_timeout(request),
            self.cache_key_func,
            cache=self.get_cache_cache(request),
            key_prefix=self.get_cache_key_prefix(request)
        )(super().dispatch)(request, *args, **kwargs)
