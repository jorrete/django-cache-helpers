import time
import datetime

from django.test import RequestFactory, TestCase
from django.http import HttpResponse
from django.core.cache import cache
from django.core.management import call_command
from django.conf import settings

from cache_helpers.decorators import cache_page_forever, cache_page


def get_key_func(request, *args, **kwargs):
    return request.path


def current_datetime(request, now):
    return HttpResponse(str(now))


settings.CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache_test',
    }
}


class CachePageDecoratorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.factory = RequestFactory()

    def test_decorator_first(self):
        """Check value of fisrt request"""
        now = datetime.datetime.now()
        request = self.factory.get('/foo/')
        response = (cache_page(1, get_key_func))(current_datetime)(request, now)
        self.assertEqual(response.content.decode('utf-8'), str(now))

    def test_decorator_second(self):
        """Check value of fisrt request"""
        time.sleep(2)
        now = datetime.datetime.now()
        request = self.factory.get('/foo/')
        response = (cache_page(1, get_key_func))(current_datetime)(request, now)
        self.assertEqual(response.content.decode('utf-8'), str(now))


class CachePageForeverDecoratorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.factory = RequestFactory()

    def test_decorator_first(self):
        """Check value of fisrt request"""
        now = datetime.datetime.now()
        request = self.factory.get('/foo/')
        response = (cache_page_forever(1, get_key_func))(current_datetime)(request, now)
        self.assertEqual(response.content.decode('utf-8'), str(now))

    def test_decorator_second(self):
        """Check value of fisrt request"""
        time.sleep(2)
        now = datetime.datetime.now()
        request = self.factory.get('/foo/')
        response = (cache_page_forever(1, get_key_func))(current_datetime)(request, now)
        self.assertNotEqual(response.content.decode('utf-8'), str(now))


class CacheClearTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.factory = RequestFactory()

    def test_decorator_first(self):
        """Check value of fisrt request"""
        now = datetime.datetime.now()
        request = self.factory.get('/foo/')
        response = (cache_page_forever(1, get_key_func))(current_datetime)(request, now)
        self.assertEqual(response.content.decode('utf-8'), str(now))

    def test_decorator_second(self):
        """Check value of fisrt request"""
        now = datetime.datetime.now()
        call_command('clear_cache', cache=['default'])
        request = self.factory.get('/foo/')
        response = (cache_page_forever(1, get_key_func))(current_datetime)(request, now)
        self.assertEqual(response.content.decode('utf-8'), str(now))
