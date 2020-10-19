from __future__ import absolute_import, unicode_literals

from .base import *  # noqa: F403,F401

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
# The SECRET_KEY below is only used in the dev and testing environment.
# It is NOT used in production (see production.py).
SECRET_KEY = 'fz08^an-s((swaouk(l+q)$ou2iina8w+1)t2yy0y9laahjh_('


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_SUBJECT_PREFIX = '[Secure the News] '

ADMINS = [
    ('John Q. Admin', 'admin@securethe.news'),
]

try:
    from .local import *  # noqa: F403,F401
except ImportError:
    pass

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        '': {
            'handlers': ['console'],
            'propagate': True,
        },
    }
}

INSTALLED_APPS.remove('django_logging')
MIDDLEWARE.remove('django_logging.middleware.DjangoLoggingMiddleware')
