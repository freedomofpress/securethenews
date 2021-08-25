from __future__ import absolute_import, unicode_literals

import structlog

from .base import *  # noqa: F403,F401


if not os.environ.get('DJANGO_DISABLE_DEBUG'):
    DEBUG = True

ALLOWED_HOSTS = ['*']
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True


timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")
shared_processors = [
    structlog.stdlib.add_log_level,
    timestamper,
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
]

# Do not cache the logger when running unit tests
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    cache_logger = False
else:
    cache_logger = True

structlog.configure(
    processors=shared_processors + [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=cache_logger,
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "normal": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
        },
        "null": {
            "class": "logging.NullHandler"
        },
    },
    "formatters": {
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
            "foreign_pre_chain": shared_processors,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["normal"], "propagate": True,
        },
        "django.template": {
            "handlers": ["normal"], "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["normal"], "propagate": False,
        },
        "django.security": {
            "handlers": ["normal"], "propagate": False,
        },
        "django.request": {
            "handlers": ["normal"],
            "propagate": False,
        },
        # Log entries from runserver
        "django.server": {
            "handlers": ["normal"], "propagate": False,
        },
        # Catchall
        "": {
            "handlers": ["normal"],
            "propagate": False,
            "level": "INFO",
        },
    },
}


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
