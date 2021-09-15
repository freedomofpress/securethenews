from __future__ import absolute_import, unicode_literals

from .base import *  # noqa: F403,F401
import os
import logging
import sys

import structlog

# This is not the Django logger; it's for reporting problems while configuring
# the app, when logging may not otherwise be set up
logging.basicConfig(format='%(levelname)s: %(message)s')

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(' ')
BASE_URL = os.environ.get('DJANGO_BASE_URL', 'https://securethe.news')


MIDDLEWARE += [  # noqa: F405
    'home.middleware.RequestLogMiddleware',
]

# Do not cache the logger when running unit tests
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    cache_logger = False
else:
    cache_logger = True

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    # Our "event_dict" is explicitly a dict
    context_class=dict,
    # Provides the logging.Logger for the underlaying log call
    logger_factory=structlog.stdlib.LoggerFactory(),
    # Provides predefined methods - log.debug(), log.info(), etc.
    wrapper_class=structlog.stdlib.BoundLogger,
    # Caching of our logger
    cache_logger_on_first_use=cache_logger,
)

pre_chain = [
    # Add the log level and a timestamp to the event_dict if the log entry
    # is not from structlog.
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "json_console": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
        },
        "null": {"class": "logging.NullHandler"},
    },
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": pre_chain,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["json_console"], "propagate": True,
        },
        "request_log": {
            "handlers": ["json_console"], "propagate": False, "level": "DEBUG",
        },
        "django.template": {
            "handlers": ["json_console"], "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["json_console"], "propagate": False,
        },
        "django.security": {
            "handlers": ["json_console"], "propagate": False,
        },
        # These are already handled by the requrest logging middleware
        "django.request": {
            "handlers": ["null"],
            "propagate": False,
        },
        # Log entries from runserver
        "django.server": {
            "handlers": ["null"], "propagate": False,
        },
        # Catchall
        "": {
            "handlers": ["json_console"], "propagate": False,
        },
    },
}


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
if os.environ.get('MAILGUN_API_KEY'):
    INSTALLED_APPS.append('anymail')  # noqa: F405
    EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'
    ANYMAIL = {
        'MAILGUN_API_KEY': os.environ['MAILGUN_API_KEY'],
        'MAILGUN_SENDER_DOMAIN': os.environ['MAILGUN_SENDER_DOMAIN'],
    }
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
    GS_FILE_OVERWRITE = os.environ.get('GS_FILE_OVERWRITE') == 'True'

    DEFAULT_FILE_STORAGE = 'securethenews.gce_storage.MediaStorage'
    if 'GS_STORE_STATIC' in os.environ:
        STATICFILES_STORAGE = 'securethenews.gce_storage.StaticStorage'
    elif 'DJANGO_STATIC_ROOT' in os.environ:
        STATIC_ROOT = os.environ['DJANGO_STATIC_ROOT']

ANALYTICS_ENABLED = True
