import time

from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from cache_helpers.decorators import cache_page_forever, cache_result
from cache_helpers.views import CachePageMixin

from myapp.caches import get_cache_key_by_path


@cache_result(3)
def expensive_func(foo=None):
    print('Expensive stuff start!!!', id, foo)
    time.sleep(1)
    print('Expensive stuff end!!!')
    return 'ok'


class Mixin(object):
    @method_decorator(cache_result(3))
    def expensive_method(self, id, foo=None):
        print('Expensive stuff start!!!', id, foo)
        time.sleep(1)
        print('Expensive stuff end!!!')
        return 'ok'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        print(self.expensive_method(3, foo='bar'))
        # print(self.expensive_method.foo)
        kwargs.update({
            'user': self.request.user,
            'lang': self.request.LANGUAGE_CODE,
        })
        return kwargs


class IndexView(Mixin, TemplateView):
    template_name = 'myapp/index.html'
    extra_context = {
        'title': 'Index',
    }


def my_cache(*args, **kwargs):
    return cache_page_forever(15, key_func=get_cache_key_by_path)


class FartView(CachePageMixin, Mixin, TemplateView):
    cache_timeout = 2
    template_name = 'myapp/index.html'
    extra_context = {
            'title': 'Fart',
            }

    def cache_key_func(self, request, *args, **kwargs):
        return request.path


@method_decorator(my_cache(), name='dispatch')
@method_decorator(never_cache, name='dispatch')
class FooView(Mixin, TemplateView):
    template_name = 'myapp/index.html'
    extra_context = {
            'title': 'Foo',
            }


@my_cache()
def bar_view(request, id, *args, **kwargs):
    print(expensive_func(5))
    return render(request, 'myapp/index.html', context={
        'title': 'Bar',
        'user': request.user,
        'lang': request.LANGUAGE_CODE,
        })
