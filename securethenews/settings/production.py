from __future__ import absolute_import, unicode_literals

from .base import *  # noqa: F403,F401
import os


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
    GS_BUCKET_NAME = os.environ.get("GS_BUCKET_NAME")
    GS_PROJECT_ID = os.environ.get("GS_PROJECT_ID")
    G_CREDS = os.environ.get("GS_CREDENTIALS", None)

    # https://github.com/jschneier/django-storages/issues/455
    if G_CREDS:
        from google.oauth2.service_account import Credentials
        GS_CREDENTIALS = Credentials.from_service_account_file(G_CREDS)

    GS_MEDIA_PATH = os.environ.get('GS_MEDIA_PATH', 'media')
    GS_STATIC_PATH = os.environ.get('GS_STATIC_PATH', 'static')

    DEFAULT_FILE_STORAGE = 'securethenews.gce_storage.MediaStorage'
    if os.environ.get("GS_STORE_STATIC", False):
        STATICFILES_STORAGE = "securethenews.gce_storage.StaticStorage"
    elif os.environ.get("DJANGO_STATIC_ROOT", False):
        STATIC_ROOT = os.environ['DJANGO_STATIC_ROOT']


# Django json logging
#

LOG_DIR = os.environ.get('DJANGO_LOG_PATH', os.path.join(BASE_DIR, 'logs'))
LOG_TO_CONSOLE = bool(os.environ.get('DJANGO_LOG_CONSOLE', False))

DJANGO_LOGGING = {
    "CONSOLE_LOG": LOG_TO_CONSOLE,
    "SQL_LOG": False,
    "DISABLE_EXISTING_LOGGERS": True,
    "PROPOGATE": False,
    "LOG_LEVEL": os.environ.get('DJANGO_LOG_LEVEL', 'info'),
    "LOG_PATH": LOG_DIR,
    "INDENT_CONSOLE_LOG": 0
}

# Ensure base log directory exists
if not os.path.exists(LOG_DIR) and not LOG_TO_CONSOLE:
    os.makedirs(LOG_DIR)
DJANGO_OTHER_LOG = os.path.join(LOG_DIR, 'django-other.log')

# Logs other than tracebacks and requests
GENERIC_LOG_HANDLER = 'rotate'
if LOG_TO_CONSOLE:
    GENERIC_LOG_HANDLER = 'console'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'json_out'
        },
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'json_out'
        },
        'null': {
            'class': 'logging.NullHandler',
        }
    },
    'formatters': {
        'json_out': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': "%(levelname)s %(created)s %(name)s "
                      "%(module)s %(message)s"
        }
    },
    'loggers': {
        'django': {
            'handlers': [GENERIC_LOG_HANDLER],
            'propagate': True,
        },
        'django.template': {
            'handlers': [GENERIC_LOG_HANDLER],
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': [GENERIC_LOG_HANDLER],
            'propagate': False,
        },
        'django.security': {
            'handlers': [GENERIC_LOG_HANDLER],
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
            'handlers': [GENERIC_LOG_HANDLER],
            'propagate': False,
        },
    },
}

if not LOG_TO_CONSOLE:
    LOGGING['handlers']['rotate'] = {
        'level': os.environ.get('DJANGO_LOG_LEVEL', 'info').upper(),
        'class': 'logging.handlers.RotatingFileHandler',
        'backupCount': 5,
        'maxBytes': 10000000,
        'filename': os.environ.get('DJANGO_LOGFILE', DJANGO_OTHER_LOG),
        'formatter': 'json_out'
    }
