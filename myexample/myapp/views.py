from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.shortcuts import render

from cache_helpers.decorators import cache_page_forever
from cache_helpers.views import CachePageMixin

from myapp.caches import get_cache_key_by_path


class Mixin(object):
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
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


@method_decorator(my_cache(), name='dispatch')
class FooView(Mixin, TemplateView):
    template_name = 'myapp/index.html'
    extra_context = {
            'title': 'Foo',
            }


class FartView(CachePageMixin, Mixin, TemplateView):
    cache_timeout = 2
    template_name = 'myapp/index.html'
    extra_context = {
            'title': 'Fart',
            }

    def cache_key_func(self, request, *args, **kwargs):
        return request.path


@my_cache()
def bar_view(request, id, *args, **kwargs):
    return render(request, 'myapp/index.html', context={
        'title': 'Bar',
        'user': request.user,
        'lang': request.LANGUAGE_CODE,
        })
