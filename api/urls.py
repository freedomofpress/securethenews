"""
Registers API URLs
"""
from . import views
from django.conf.urls import url
from django.views.generic import RedirectView

urlpatterns = [
    # We'll always redirect to the latest version; version should be an integer
    # and changed only for breaking changes
    url(r'^$', RedirectView.as_view(url='/api/v1')),
    url(r'v1/$', views.api_root, name='api-root-v1'),
    url(r'v1/sites/$', views.SiteList.as_view(), name='site-list'),
    # Standard lookup would be primary key, but we want lookup by domain
    url(r'v1/sites/(?P<domain>.+)/scans/$',
        views.ScanList.as_view(), name='scan-list'),
    url(r'v1/sites/(?P<domain>.+)/$',
        views.SiteDetail.as_view(), name='site-detail'),
]
