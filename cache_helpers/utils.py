import math
import threading

from django.core.cache import caches

from .settings import CACHE_HELPERS_ALIAS


CACHE_HELPERS_KEY = 'cache_helpers_key'


def set_cache_bust_status(bust_key=None):
    cache = caches[CACHE_HELPERS_ALIAS]
    cache.set(CACHE_HELPERS_KEY, bust_key)


def get_bust_key():
    cache = caches[CACHE_HELPERS_ALIAS]
    return cache.get(CACHE_HELPERS_KEY, None)


def mark_response_as_processed(response):
    setattr(response, '_already_cahed', True)


def check_response_has_been_processed(response):
    return getattr(response, '_already_cahed', False)


def check_bust_header(request):
    bust_key = request.META.get('HTTP_BUST', '')
    return False if (not bust_key or bust_key != get_bust_key()) else True


# TODO avoid list user generator
def threaded_cue(cue, callback, threads):
    def process_chunk(begining, end, worker_num):
        for index, item in enumerate(cue[begining:end]):
            real_index = (begining + index) if begining > 0 else index
            result = callback(item)
            if result:
                cue[real_index] = result

    CHUNK_SIZE = math.ceil(len(cue) / threads)
    end = 0

    threads_refs = []

    for i in range(threads):
        begining = end
        end = begining + CHUNK_SIZE
        t = threading.Thread(target=process_chunk, args=(begining, end if end < len(cue) else len(cue), i))
        t.start()
        threads_refs.append(t)

    for i in threads_refs:
        t.join()

    return cue


def get_ref_from_func(func):
    if hasattr(func, '__self__'):
        return func.__self__.__class__
    return func


def get_func_from_func(func):
    if hasattr(func, '__wrapped__'):
        return func.__wrapped__
    return func


def func_to_string(func):
    func = func.func if hasattr(func, 'func') else func

    ref = get_ref_from_func(func)

    chunks = [
        ref.__module__,
        ref.__name__,
    ]

    func = get_func_from_func(func)

    if func.__name__ != chunks[-1]:
        chunks.append(func.__name__)

    return '.'.join(chunks)


def invalidate_cache(cache_key, cache=None):
    cache = caches[cache if cache is not None else CACHE_HELPERS_ALIAS]
    cache.delete(cache_key)
