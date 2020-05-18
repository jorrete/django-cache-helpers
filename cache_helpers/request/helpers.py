from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class BaseRequestMixin:
    basic_auth = None
    langs = []
    login = None
    threads = 1
    urls = []

    def get_request_basic_auth(self):
        return self.basic_auth

    def get_request_langs(self):
        return self.langs

    def get_request_login(self):
        return self.login

    def get_request_treads(self):
        return self.threads

    def get_request_urls(self):
        return self.urls

    def get_request_runner(self):
        raise NotImplementedError()

    def make_requests(self):
        langs = self.get_request_langs()
        runner = self.get_request_runner()

        if not len(langs):
            runner(
                threads=self.get_request_treads(),
                urls=self.get_request_urls(),
                basic_auth=self.get_request_basic_auth(),
                login=self.get_request_login())
        else:
            for lang in self.get_request_langs():
                runner(
                    threads=self.get_request_treads(),
                    urls=self.get_request_urls(),
                    basic_auth=self.get_request_basic_auth(),
                    login=self.get_request_login(),
                    lang=lang)


class BaseRequestCommand(BaseRequestMixin, BaseCommand):
    help = 'Make requests.'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Make requests to warm up caches'))
            self.make_requests()
        except Exception as e:
            if settings.DEBUG:
                raise e
            raise CommandError(e)
