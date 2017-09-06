from django.conf.urls import url

from . import views

app_name = 'pledges'
urlpatterns = [
    url(r'^$', views.pledge, name='pledge'),
    url(r'^thanks$', views.thanks, name='thanks'),
    url(r'^(?P<pk>[0-9]+)/confirm$', views.confirm, name='confirm'),
    url(r'^(?P<pk>[0-9]+)/confirmed$', views.confirmed, name='confirmed'),
]
