from __future__ import absolute_import, unicode_literals

from .base import *  # noqa: F403,F401
import os
import sys
import logging

# This is not the Django logger; it's for reporting problems while configuring
# the app, when logging may not otherwise be set up
logging.basicConfig(format='%(levelname)s: %(message)s')

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(' ')
BASE_URL = os.environ.get('DJANGO_BASE_URL', 'https://securethe.news')

try:
    CSRF_TRUSTED_ORIGINS = os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'].split(' ')
except KeyError:
    pass

try:
    from .local import *  # noqa: F403,F401
except ImportError:
    pass

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DJANGO_DB_NAME', 'stn'),
        'USER': os.environ['DJANGO_DB_USER'],
        'PASSWORD': os.environ['DJANGO_DB_PASSWORD'],
        'HOST': os.environ['DJANGO_DB_HOST'],
        'PORT': os.environ['DJANGO_DB_PORT']
    }
}


try:
    es_host = os.environ.get('DJANGO_ES_HOST', 'disable')

    if es_host == 'disable':
        WAGTAILSEARCH_BACKENDS = {}
    else:
        WAGTAILSEARCH_BACKENDS = {
            'default': {
                'BACKEND': 'wagtail.search.backends.elasticsearch2',
                'URLS': [es_host],
                'INDEX': 'wagtail',
                'TIMEOUT': 5,
                'OPTIONS': {
                    'ca_certs': os.environ['DJANGO_ES_CA_PATH'],
                    'use_ssl': True,
                },
            }
        }
except KeyError:
    pass

WEBPACK_LOADER['DEFAULT']['CACHE'] = True  # noqa: F405

# Mailgun integration
#
if os.environ.get('MAILGUN_ACCESS_KEY'):
    EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
    MAILGUN_ACCESS_KEY = os.environ.get('MAILGUN_ACCESS_KEY')
    MAILGUN_SERVER_NAME = os.environ.get('MAILGUN_SERVER_NAME')
    DEFAULT_FROM_EMAIL = os.environ.get('MAILGUN_FROM_ADDR',
                                        'webmaster@mg.securethe.news')


# Cloudflare caching
#
if os.environ.get('CLOUDFLARE_TOKEN') and os.environ.get('CLOUDFLARE_EMAIL'):
    INSTALLED_APPS.append('wagtail.contrib.frontend_cache')  # noqa: F405
    WAGTAILFRONTENDCACHE = {
        'cloudflare': {
            'BACKEND': 'wagtail.contrib.frontend_cache.backends.CloudflareBackend',  # noqa: E501
            'EMAIL': os.environ.get('CLOUDFLARE_EMAIL'),
            'TOKEN': os.environ.get('CLOUDFLARE_TOKEN'),
            'ZONEID': os.environ.get('CLOUDFLARE_ZONEID')
        },
    }

# Piwik analytics, via django-analytical
# https://pythonhosted.org/django-analytical/install.html
if os.environ.get('PIWIK_DOMAIN_PATH'):
    PIWIK_DOMAIN_PATH = os.environ.get('PIWIK_DOMAIN_PATH')
    PIWIK_SITE_ID = os.environ.get('PIWIK_SITE_ID', '1')


if os.environ.get('AWS_SESSION_TOKEN'):
    INSTALLED_APPS.append('storages')  # noqa: F405

    AWS_S3_MEDIA_PATH = os.environ.get('AWS_S3_MEDIA_PATH', 'media')
    AWS_S3_STATIC_PATH = os.environ.get('AWS_S3_STATIC_PATH', 'static')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_SESSION_TOKEN = os.environ.get('AWS_SESSION_TOKEN', '')
    AWS_S3_USE_SSL = True
    AWS_S3_SIGNATURE_VERSION = os.environ.get("AWS_S3_SIG_VER", "s3v4")
    STATICFILES_STORAGE = "securethenews.s3_storage.StaticStorage"
    DEFAULT_FILE_STORAGE = "securethenews.s3_storage.MediaStorage"

elif os.environ.get('GS_BUCKET_NAME'):
    INSTALLED_APPS.append('storages')  # noqa: F405

    if 'GS_CREDENTIALS' in os.environ:
        from google.oauth2.service_account import Credentials
        gs_creds_path = os.environ['GS_CREDENTIALS']
        GS_CREDENTIALS = Credentials.from_service_account_file(gs_creds_path)
    elif 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
        logging.warning('Defaulting to global GOOGLE_APPLICATION_CREDENTIALS')
    else:
        logging.warning(
            'GS_CREDENTIALS or GOOGLE_APPLICATION_CREDENTIALS unset! ' +
            'Falling back to credentials of the machine we are running on, ' +
            'if it is a GCE instance. This is almost certainly not desired.'
        )

    # Optional setting; we generally do not need to use a bucket that lives in
    # a different project, so this will be unset
    if 'GS_PROJECT_ID' in os.environ:
        GS_PROJECT_ID = os.environ['GS_PROJECT_ID']

    GS_BUCKET_NAME = os.environ['GS_BUCKET_NAME']
    GS_MEDIA_PATH = os.environ.get('GS_MEDIA_PATH', 'media')
    GS_STATIC_PATH = os.environ.get('GS_STATIC_PATH', 'static')

    DEFAULT_FILE_STORAGE = 'securethenews.gce_storage.MediaStorage'
    if 'GS_STORE_STATIC' in os.environ:
        STATICFILES_STORAGE = 'securethenews.gce_storage.StaticStorage'
    elif 'DJANGO_STATIC_ROOT' in os.environ:
        STATIC_ROOT = os.environ['DJANGO_STATIC_ROOT']


# Django json logging

log_handlers = {
    'debug': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'json_out'
    },
    'null': {
        'class': 'logging.NullHandler',
    }
}

django_logfile = os.environ.get('DJANGO_LOGFILE')
log_level = os.environ.get('DJANGO_LOG_LEVEL', 'info').upper()

if django_logfile:
    console_log = False
    # Ensure base log directory exists
    log_dir = os.path.dirname(django_logfile)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_handler = 'rotate'
    log_handlers['rotate'] = {
        'level': log_level,
        'class': 'logging.handlers.RotatingFileHandler',
        'backupCount': 5,
        'maxBytes': 10000000,
        'filename': django_logfile,
        'formatter': 'json_out'
    }
else:
    console_log = True
    log_handler = 'console'
    log_handlers['console'] = {
        'level': log_level,
        'class': 'logging.StreamHandler',
        'formatter': 'json_out',
        'stream': sys.stdout,
    }

DJANGO_LOGGING = {
    "CONSOLE_LOG": console_log,
    "SQL_LOG": False,
    "DISABLE_EXISTING_LOGGERS": True,
    "PROPOGATE": False,
    "LOG_LEVEL": log_level,
    "INDENT_CONSOLE_LOG": 0
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': log_handlers,
    'formatters': {
        'json_out': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': "%(levelname)s %(created)s %(name)s "
                      "%(module)s %(message)s"
        }
    },
    'loggers': {
        'django': {
            'handlers': [log_handler],
            'propagate': True,
        },
        'django.template': {
            'handlers': [log_handler],
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': [log_handler],
            'propagate': False,
        },
        'django.security': {
            'handlers': [log_handler],
            'propagate': False,
        },
        # These are already handled by the django json logging library
        'django.request': {
            'handlers': ['null'],
            'propagate': False,
        },
        # Log entries from runserver
        'django.server': {
            'handlers': ['null'],
            'propagate': False,
        },
        '': {
            'handlers': [log_handler],
            'propagate': False,
        },
    },
}
