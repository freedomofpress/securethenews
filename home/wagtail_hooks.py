from wagtail.core import hooks
from django.conf.urls import url

from .views import deploy_info_view


@hooks.register('register_admin_urls')
def urlconf_time():
    return [
        url(r'^version/?$', deploy_info_view, name='deployinfo'),
    ]
