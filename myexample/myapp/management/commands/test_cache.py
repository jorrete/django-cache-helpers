from cache_helpers.request import RequestCommand


class Command(RequestCommand):
    login = {
        'url': 'http://192.168.1.10:9000/admin/login/',
        'username': 'admin',
        'password': 'admin',
    }
    urls = [
            'http://192.168.1.10:9000/',
            'http://192.168.1.10:9000/foo/',
    ]
