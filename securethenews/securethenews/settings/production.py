from __future__ import absolute_import, unicode_literals

from .base import *
import os

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

try:
    from .local import *
except ImportError:
    pass

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'fpf',
        'USER': os.environ['DJANGO_DB_USER'],
        'PASSWORD': os.environ['DJANGO_DB_PASSWORD'],
        'HOST': os.environ['DJANGO_DB_HOST'],
        'PORT': os.environ['DJANGO_DB_PORT']
    }
}

STATIC_ROOT = os.environ['DJANGO_STATIC_ROOT']
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'client', 'build')
]

try:
    es_host = os.environ.get('DJANGO_ES_HOST', 'disable')

    if es_host == 'disable':
        WAGTAILSEARCH_BACKENDS = {}
    else:
        WAGTAILSEARCH_BACKENDS = {
            'default': {
                'BACKEND': 'wagtail.wagtailsearch.backends.elasticsearch2',
                'URLS': [es_host],
                'INDEX': 'wagtail',
                'TIMEOUT': 5
            }
        }

        WAGTAILSEARCH_BACKENDS['default']['ca_certs'] = os.environ['DJANGO_ES_CA_PATH']
        WAGTAILSEARCH_BACKENDS['default']['use_ssl'] = True
except KeyError:
    pass
