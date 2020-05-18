from cache_helpers.request.real import RealRequestCommand


class Command(RealRequestCommand):
    login = {
        'url': 'http://192.168.1.5:9000/admin/login/',
        'username': 'admin',
        'password': 'admin',
    }
    langs = ['de', 'it']
    urls = [
            'http://192.168.1.5:9000/',
            'http://192.168.1.5:9000/foo/',
    ]
