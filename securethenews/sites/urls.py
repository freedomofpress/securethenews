from django.conf.urls import url

from . import views

app_name = 'sites'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pledge$', views.pledge, name='pledge'),
    url(r'^pledge/thanks$', views.pledge_thanks, name='pledge_thanks'),
    url(r'^pledge/(?P<pk>[0-9]+)/confirm$', views.confirm_pledge,
        name='confirm_pledge'),
    url(r'^pledge/(?P<pk>[0-9]+)/confirmed$', views.pledge_confirmed,
        name='pledge_confirmed'),
    url(r'^(?P<slug>[\w-]+)$', views.site, name='site'),
]
