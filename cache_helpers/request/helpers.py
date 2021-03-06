import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ..utils import threaded_cue


class BaseRequestMixin:
    request_always_anonymous = False
    request_basic_auth = None
    request_langs = []
    request_login = None
    request_threads = 1
    request_urls = []

    def get_request_always_anonymous(self):
        return self.request_always_anonymous

    def get_request_basic_auth(self):
        return self.request_basic_auth

    def get_request_langs(self):
        return self.request_langs

    def get_request_login(self):
        return self.request_login

    def get_request_treads(self):
        return self.request_threads

    def get_request_urls(self):
        return self.request_urls

    def _get_request_urls(self):
        if not hasattr(self, '_cached_request_urls'):
            setattr(self, '_cached_request_urls', self.get_request_urls())
        return getattr(self, '_cached_request_urls')

    def get_request_runner(self):
        raise NotImplementedError()

    def _make_requests(self, login=None, threads=1, urls=None, **extra):
        runner = self.get_request_runner()
        urls = urls if urls is not None else self._get_request_urls()
        langs = self.get_request_langs()

        def callback(url):
            for lang in (langs if len(langs) else [None]):
                runner(
                    url=url,
                    basic_auth=self.get_request_basic_auth(),
                    login=login,
                    lang=lang,
                    **extra)

        threaded_cue(urls, callback, threads)
        return len(urls)

    def make_requests(self, threads=1, urls=None, **extra):
        logins = [self.get_request_login()]
        if self.get_request_always_anonymous() and None not in logins:
            logins.insert(0, None)

        for login in logins:
            self._make_requests(login=login, threads=threads, urls=urls, **extra)


class BaseRequestCommand(BaseRequestMixin, BaseCommand):
    help = 'Make requests.'

    def add_arguments(self, parser):
        parser.add_argument('--threads', nargs='?',
                            type=int, default=1,
                            help='Number of threads')

    def handle(self, *args, **options):
        try:
            urls = self._get_request_urls()
            threads = options['threads'] if 'threads' in options else self.get_request_treads()
            start = time.time()
            self.stdout.write(self.style.SUCCESS('Make requests to warm up caches with {} threads'.format(threads)))
            self.make_requests(threads=threads)
            done = time.time()
            elapsed = done - start
            self.stdout.write(self.style.SUCCESS('Make requests done: {} urls in {}s'.format(
                len(urls), elapsed)))
        except Exception as e:
            if settings.DEBUG:
                raise e
            raise CommandError(e)
