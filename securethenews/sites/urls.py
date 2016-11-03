from django.conf.urls import url

from . import views

app_name = 'sites'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^pledge$', views.pledge, name='pledge'),
    url(r'^pledge/thanks$', views.pledge_thanks, name='pledge_thanks'),
    url(r'^(?P<slug>[\w-]+)$', views.site, name='site'),
]
