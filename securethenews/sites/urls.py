from django.conf.urls import url

from . import views

urlpatterns = [
    # /sites/
    url(r'^$', views.index, name='index'),
    # /sites/110
    url(r'^(?P<pk>[0-9]+)', views.detail, name='detail'),
    # /sites/110/new-york-times
    url(
        r'^(?P<pk>[0-9]+)/[A-Za-z0-9\-]+/?$',
        views.detail,
        name='detail'
    ),
]
