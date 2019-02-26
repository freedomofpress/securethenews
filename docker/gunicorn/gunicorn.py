import os

user = os.environ.get('DJANGO_GCORN_USER', 'gcorn')
group = os.environ.get('DJANGO_GCORN_GROUP', 'gcorn')
bind = os.environ.get('DJANGO_GCORN_BIND', '0.0.0.0:8000')
loglevel = os.environ.get('DJANGO_GCORN_LOGLEVEL', 'debug')
capture_output = os.environ.get('DJANGO_GCORN_CAPOUTPUT', False)
# See http://docs.gunicorn.org/en/stable/design.html for deployment
# considerations. Using threads assumes use of the gthread worker which
# is not the default.
workers = int(os.environ.get('DJANGO_GCORN_WORKERS', 6))
threads = int(os.environ.get('DJANGO_GCORN_THREADS', 1))

# Log gunicorn events to console if specified user env supplied
if os.environ.get('DJANGO_LOG_CONSOLE', "n").lower() in ['y', '1', 'yes']:
    logconfig_dict = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'jsonconsole': {
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
            'gunicorn.access': {
                'handlers': ['null'],
            },
            'gunicorn.error': {
                'handlers': ['jsonconsole'],
                'level': 'INFO',
            },
        },
    }
