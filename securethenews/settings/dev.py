from __future__ import absolute_import, unicode_literals

from .base import *  # noqa: F403,F401


if not os.environ.get('DJANGO_DISABLE_DEBUG'):
    DEBUG = True

ALLOWED_HOSTS = ['*']
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True


# The example SECRET_KEY below is used only in the local dev env.
# In the production settings file, a custom env var is required
# to run the application.
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
