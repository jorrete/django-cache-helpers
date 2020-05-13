# django-cache-helpers (alpha)

## Install

```bash
pip install django-cache-helpers
```

## Description

Few helpers to have more control over django cache.

## decorators

### cache_page

```python
# my_app/views.py
from django.http import HttpResponse
from cache_helpers.decorators import cache_page

def my_key_func(request):
    return request.path

@cache_page(60, my_key_func, cache=None, key_prefix=None)
def my_view(request):
    html = "<html><body></body></html>"
    return HttpResponse(html)
```

It's like the cache_page decorator but it expects a funcion as **key_func** argument that must return the cache key.

### cache_page_forever

```python
# my_app/views.py
from django.http import HttpResponse
from cache_helpers.decorators import cache_page

def my_key_func(request):
    return request.path

@cache_page_forever(60, my_key_func, cache=None, key_prefix=None)
def my_view(request):
    html = "<html><body></body></html>"
    return HttpResponse(html)
```

The use of this decorator is to prevent that very expensive requests are ever hit by a user.

This decorator expects same arguments that cache_page but it will be cached forever setting the timeout to None in the cache. Yo still pass timeout because it will used to set the **expire** header (**max-age** will be omitted) in the response object.
To update the cache you will use a custom command that will use **cache_helpers.request.RequestCommand** mixin (look at example).

The combination of **cache_page_forever** and the custom command will prevent any **cache stampede** and you will offload these heavy requests to a command with a **cron job** or an **asynchronous task**.

## views

## CachePageMixin

Mixin to apply **cache_page** to dispatch.

```python
# my_app/views.py
from django.views.generic import View
from cache_helpers.views import CachePageMixin

def my_key_func(request):
    return request.path

class MyView(CachePageMixin, View):
    cache_timeout = 3600
    cache_key_func = my_key_func
    cache_key_prefix = None
    cache_cache = None
```

## CachePageForeverMixin

Mixin to apply **cache_page_forever** to dispatch.

```python
# my_app/views.py
from django.views.generic import View
from cache_helpers.views import CachePageForeverMixin

def my_key_func(request):
    return request.path

class MyView(CachePageForeverMixin, View):
    cache_timeout = 3600
    cache_key_func = my_key_func
    cache_key_prefix = None
    cache_cache = None
```

## request

## make_requests

```python
# my_app/some_file.py
from cache_helpers.request import make_requests

urls = [
    'http://localhost:9000/',
    'http://localhost:9000/foo/',
]
basic_auth = {
    'username': 'myuser',
    'password': 'mypass',
}
login = {
    'url': 'http://localhost:9000/admin/login/',
    'username': 'admin',
    'password': 'admin',
}
make_requests(threads=1, urls=urls, basic_auth=basic_auth, login=login)
```

Function that will make requests to warm up or renew caches. It handles basic http auth and login against django auth.

It may look contradictory to allow to warm up caches with a registered user "manually" but maybe you have a **single-page app** common UI for registered users and a different for the **anonymous** user. If that is the case, create dumb user without privileges for this case.

It's multhreaded to speed up the process.

To renew **cache_page_forever** views it's mandatory use this helper.

## RequestMixin

Mixin helper.

```python
# my_app/some_file.py
from cache_helpers.request import RequestMixin

class MyObject(RequestMixin):
    urls = [
        'http://localhost:9000/',
        'http://localhost:9000/foo/',
    ]
    basic_auth = {
        'username': 'myuser',
        'password': 'mypass',
    }
    login = {
        'url': 'http://localhost:9000/admin/login/',
        'username': 'admin',
        'password': 'admin',
    }

foo = MyObject()
foo.make_requests()
```

## RequestCommand

Command helper.

```python

# my_app/management/commands/warmup_my_urls.py
from cache_helpers.request import RequestCommand

class WarmupMyUrlsCommand(RequestCommand):
    urls = [
        'http://localhost:9000/',
        'http://localhost:9000/foo/',
    ]
    basic_auth = {
        'username': 'myuser',
        'password': 'mypass',
    }
    login = {
        'url': 'http://localhost:9000/admin/login/',
        'username': 'admin',
        'password': 'admin',
    }
```

```bash
./manage.py warmup_my_urls
```

## commands

## clear_cache

Command to clear caches.

Accepts a list of cache alias as **cache** argument.

```bash
./manage.py clear_cache --cache default foo
```

If it's called without --cache flag it will clear all caches configured in settings.CACHES.

```bash
./manage.py clear_cache
```

## Development

### Install

```bash
git clone https://github.com/jorrete/django-cache-helpers
cd django-cache-helpers/myexample
./create_venv
. venv/bin/activate
./manage.py runserver
```

### Test

```bash
cd django-cache-helpers
tox
```
