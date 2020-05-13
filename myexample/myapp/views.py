from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

from cache_helpers.decorators import cache_page_forever


class Mixin(object):
    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs.update({
            'user': self.request.user,
        })
        return kwargs


class IndexView(Mixin, TemplateView):
    template_name = 'myapp/index.html'
    extra_context = {
        'title': 'Index',
    }


def get_cache_key(request, *args):
    return request.path


@method_decorator(cache_page_forever(15, key_func=get_cache_key), name='dispatch')
class FooView(Mixin, TemplateView):
    template_name = 'myapp/index.html'
    extra_context = {
        'title': 'Foo',
    }
