from cache_helpers.request.real import RealRequestCommand


class Command(RealRequestCommand):
    request_always_anonymous = True
    request_login = {
        'url': 'http://192.168.1.5:9000/admin/login/',
        'username': 'admin',
        'password': 'admin',
    }
    request_langs = ['de', 'it']
    request_threads = 1
    request_urls = [
        'http://192.168.1.5:9000/',
        'http://192.168.1.5:9000/foo/',
        'http://192.168.1.5:9000/bar/',
    ]
