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
                'BACKEND': 'wagtail.wagtailsearch.backends.elasticsearch2',
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
    INSTALLED_APPS.append('wagtail.contrib.wagtailfrontendcache')  # noqa: F405
    WAGTAILFRONTENDCACHE = {
        'cloudflare': {
            'BACKEND': 'wagtail.contrib.wagtailfrontendcache.backends.CloudflareBackend',  # noqa: E501
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

else:
    STATIC_ROOT = os.environ['DJANGO_STATIC_ROOT']
    MEDIA_ROOT = os.environ['DJANGO_MEDIA_ROOT']
