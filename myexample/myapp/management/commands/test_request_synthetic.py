from cache_helpers.request.synthetic import SyntheticRequestCommand


class Command(SyntheticRequestCommand):
    request_always_anonymous = True
    request_login = {'username': '', }
    request_langs = ['de', 'it']
    request_threads = 1
    request_urls = [
        'http://192.168.1.5:9000/',
        'http://192.168.1.5:9000/foo/',
        'http://192.168.1.5:9000/bar/',
    ]
