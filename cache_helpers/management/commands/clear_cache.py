from django.conf import settings
from django.core.cache import caches
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """A simple management command which clears the site-wide cache."""
    help = 'Fully clear your site-wide cache.'

    def add_arguments(self, parser):
        parser.add_argument('-c', '--cache', nargs='*', default=[], help='List of caches alias.')

    def handle(self, *args, **kwargs):
        try:
            assert settings.CACHES
            cache_list = kwargs.get('cache', [])
            cache_list = cache_list if len(cache_list) else settings.CACHES.keys()
            for cache_name in cache_list:
                assert settings.CACHES[cache_name]
                caches[cache_name].clear()
                self.stdout.write('Cache "{}" has been cleared!\n'.format(cache_name))
        except AttributeError:
            raise CommandError('You caches are not configured!\n')
        except KeyError as e:
            raise CommandError('You have no cache "{}" configured!\n'.format(str(e)))
