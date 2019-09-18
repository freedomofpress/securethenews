from django.conf.urls import url

from . import views

app_name = 'sites'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<slug>[\w-]+)$', views.site, name='site'),
    url(r'^leaderboard/(?P<slug>[\w-]+)$', views.leaderboard,
        name='leaderboard'),
]
