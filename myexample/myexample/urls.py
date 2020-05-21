"""myexample URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from myapp.views import IndexView, FooView, bar_view, FartView
from cache_helpers.decorators import cache_page
from myapp.caches import get_cache_key_by_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('foo/<int:id>/', FooView.as_view(), name='foo'),
    path('fart/<int:id>/', FartView.as_view(), name='fart'),
    path('bar/<int:id>/', bar_view, name='bar'),
    path('', cache_page(3, key_func=get_cache_key_by_view)(IndexView.as_view()), name='index'),
]
