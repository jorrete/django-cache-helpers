from cache_helpers.request.synthetic import SyntheticRequestCommand


class Command(SyntheticRequestCommand):
    login = {
        'username': '',
    }
    langs = ['de', 'it']
    urls = [
        'http://192.168.1.5:9000/',
        'http://192.168.1.5:9000/foo/',
        'http://192.168.1.5:9000/bar/',
    ]
