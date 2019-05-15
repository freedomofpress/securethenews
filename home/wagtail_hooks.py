from wagtail.core import hooks
from django.conf.urls import url

from .views import gitinfo_view


@hooks.register('register_admin_urls')
def urlconf_time():
    return [
        url(r'^gitinfo/$', gitinfo_view, name='gitinfo'),
    ]
