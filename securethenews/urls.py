from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from wagtailautocomplete.urls.admin import urlpatterns \
    as autocomplete_admin_urls
from wagtailautocomplete.views import objects, search

from search import views as search_views
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

autocomplete_public_urls = [
    path('objects/', objects),
    path('search/', search),
]

urlpatterns = [
    path('django-admin/', admin.site.urls),

    path('autocomplete/', include(autocomplete_public_urls)),
    path('admin/autocomplete/', include(autocomplete_admin_urls)),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    path('search/', search_views.search, name='search'),

    path('sites/', include('sites.urls')),
    path('news/', include('blog.urls')),
    path('api/', include('api.urls')),

    path('', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
