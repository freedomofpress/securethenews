import os
import re

import structlog

user = os.environ.get('DJANGO_GCORN_USER', 'gcorn')
group = os.environ.get('DJANGO_GCORN_GROUP', 'gcorn')
bind = os.environ.get('DJANGO_GCORN_BIND', '0.0.0.0:8000')
loglevel = os.environ.get('DJANGO_GCORN_LOGLEVEL', 'INFO')
capture_output = os.environ.get('DJANGO_GCORN_CAPOUTPUT', False)
# See http://docs.gunicorn.org/en/stable/design.html for deployment
# considerations. Using threads assumes use of the gthread worker which
# is not the default.
workers = int(os.environ.get('DJANGO_GCORN_WORKERS', 6))
threads = int(os.environ.get('DJANGO_GCORN_THREADS', 1))
tmp_upload_dir = os.environ.get('DJANGO_GCORN_UPLOAD_DIR', None)
worker_tmp_dir = os.environ.get('DJANGO_GCORN_HEARTBT_DIR', None)


def combined_logformat(logger, name, event_dict):
    if event_dict.get('logger') == "gunicorn.access":
        message = event_dict['event']

        parts = [
            r'(?P<host>\S+)',       # host %h
            r'\S+',                 # indent %l (unused)
            r'(?P<user>\S+)',       # user %u
            r'\[(?P<time>.+)\]',    # time %t
            r'"(?P<request>.+)"',   # request "%r"
            r'(?P<status>[0-9]+)',  # status %>s
            r'(?P<size>\S+)',       # size %b (careful, can be '-')
            r'"(?P<referer>.*)"',   # referer "%{Referer}i"
            r'"(?P<agent>.*)"',     # user agent "%{User-agent}i"
        ]
        pattern = re.compile(r'\s+'.join(parts) + r'\s*\Z')
        m = pattern.match(message)
        res = m.groupdict()

        if res["user"] == "-":
            res["user"] = None

        res["status"] = int(res["status"])

        if res["size"] == "-":
            res["size"] = 0
        else:
            res["size"] = int(res["size"])

        if res["referer"] == "-":
            res["referer"] = None

        event_dict.update(res)

    return event_dict


# Structlog logging initialisation code
timestamper = structlog.processors.TimeStamper(fmt="iso")
pre_chain = [
    # Add the log level and a timestamp to the event_dict if the log entry
    # is not from structlog.
    structlog.stdlib.add_log_level,
    structlog.stdlib.add_logger_name,
    timestamper,
    combined_logformat,
]

logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": pre_chain,
        }
    },
    "handlers": {
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
        },
        "null": {
            "class": "logging.NullHandler"
        },
    },
    "loggers": {
        "gunicorn.access": {
            "handlers": ["null"], "propagate": False,
        },
        "gunicorn.error": {
            "handlers": ["console"], "propagate": False,
        },
    }
}
