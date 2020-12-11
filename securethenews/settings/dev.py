from __future__ import absolute_import, unicode_literals

from .base import *  # noqa: F403,F401

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
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
