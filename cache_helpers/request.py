import math
import threading
import requests
import logging
import uuid

from django.core.management.base import BaseCommand, CommandError

from .utils import set_cache_bust_status


logger = logging.getLogger(__name__)


def threaded_cue(cue, callback, threads):
    def process_chunk(begining, end):
        for index, item in enumerate(cue[begining:end]):
            real_index = (begining + index) if begining > 0 else index
            result = callback(item)
            if result:
                cue[real_index] = result

    CHUNK_SIZE = math.ceil(len(cue) / threads)
    end = 0

    for i in range(threads):
        begining = end
        end = begining + CHUNK_SIZE
        t = threading.Thread(target=process_chunk, args=(begining, end if end < len(cue) else len(cue)))
        t.start()
        t.join()

    return cue


def make_requests(threads=1, urls=[], basic_auth=None, login=None):
    try:
        session = requests.session()
        bust_key = str(uuid.uuid4())
        set_cache_bust_status(bust_key)

        def callback(url):
            try:

                kwargs = {
                    'headers': {
                        'bust': bust_key
                    }
                }

                if basic_auth:
                    kwargs['auth'] = (basic_auth['username'], basic_auth['password'])
                session.get(url, **kwargs)
                logger.info('Request success: {}'.format(url))
            except Exception as e:
                logger.error('Request error: {}'.format(url))
                raise e

        if login:
            req = session.get(login['url'])
            req = session.post(login['url'], data={
                'username': login['username'],
                'password': login['password'],
                'csrfmiddlewaretoken': req.cookies['csrftoken'],
                'next': login['url'],
            })

            if req.status_code >= 300:
                raise Exception('Login failed')
            else:
                logger.info('Login success')

        threaded_cue(urls, callback, threads)
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        set_cache_bust_status()


class RequestMixin:
    threads = 1
    urls = []
    basic_auth = None
    login = None

    def get_urls(self):
        return self.urls

    def get_basic_auth(self):
        return self.basic_auth

    def get_login(self):
        return self.login

    def make_requests(self):
        make_requests(threads=self.threads, urls=self.urls, basic_auth=self.basic_auth, login=self.login)


class RequestCommand(RequestMixin, BaseCommand):
    help = 'Make requests.'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Make requests to warm up caches'))
            self.make_requests()
        except Exception as e:
            CommandError(e)
