from __future__ import absolute_import, unicode_literals

from .base import *
import os


DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(' ')

try:
    CSRF_TRUSTED_ORIGINS = os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'].split(' ')
except KeyError:
    pass

try:
    from .local import *
except ImportError:
    pass

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'stn',
        'USER': os.environ['DJANGO_DB_USER'],
        'PASSWORD': os.environ['DJANGO_DB_PASSWORD'],
        'HOST': os.environ['DJANGO_DB_HOST'],
        'PORT': os.environ['DJANGO_DB_PORT']
    }
}

STATIC_ROOT = os.environ['DJANGO_STATIC_ROOT']
MEDIA_ROOT = os.environ['DJANGO_MEDIA_ROOT']

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

# Django json logging
#
if os.environ.get('DJANGO_JSON_LOG', 'no').lower() in ['true', 'yes']:
    INSTALLED_APPS.append('django_logging')
    MIDDLEWARE_CLASSES.append('django_logging.middleware.DjangoLoggingMiddleware')
    DJANGO_LOGGING = {
        "CONSOLE_LOG": False,
        "SQL_LOG": False,
        "LOG_LEVEL": os.environ.get('DJANGO_LOG_LEVEL', 'info')
    }
elif os.environ.get('DJANGO_LOG', 'no').lower() in ['true', 'yes']:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'rotate': {
                'level': os.environ.get('DJANGO_LOG_LEVEL', 'info').upper(),
                'class': 'logging.handlers.RotatingFileHandler',
                'backupCount': 5,
                'maxBytes': 10000000,
                'filename': os.environ.get('DJANGO_LOGFILE',
                                           '/var/log/securethenews/django.log')
            },
        },
        'loggers': {
            '': {
                'handlers': ['rotate'],
                'level': os.environ.get('DJANGO_LOG_LEVEL', 'info').upper(),
                'propagate': True,
            },
        },
    }

# Cloudflare caching
#
if os.environ.get('CLOUDFLARE_TOKEN') and os.environ.get('CLOUDFLARE_EMAIL'):
    WAGTAILFRONTENDCACHE = {
        'cloudflare': {
            'BACKEND': 'ops.utils.CloudflareBackend',
            'EMAIL': os.environ.get('CLOUDFLARE_EMAIL'),
            'TOKEN': os.environ.get('CLOUDFLARE_TOKEN'),
            'ZONEID': os.environ.get('CLOUDFLARE_ZONEID')
        },
    }
