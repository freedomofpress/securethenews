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
tmp_upload_dir = os.environ.get('DJANGO_GCORN_UPLOAD_DIR', None)
worker_tmp_dir = os.environ.get('DJANGO_GCORN_HEARTBT_DIR', None)
