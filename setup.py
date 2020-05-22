from setuptools import setup

setup(name='django-cache-helpers',
      version='0.1.0',
      description='',
      url='https://github.com/jorrete/django-cache-helpers/',
      author='Jorge Rodríguez-Flores Esparza',
      author_email='jorrete@gmail.com',
      license='MIT',
      packages=['cache_helpers', ],
      include_package_data=True,
      install_requires=[
          'requests',
      ],
      zip_safe=False)
