import os

user = os.environ.get('DJANGO_GCORN_USER', 'gcorn')
group = os.environ.get('DJANGO_GCORN_GROUP', 'gcorn')
bind = os.environ.get('DJANGO_GCORN_BIND', '0.0.0.0:8000')
loglevel = os.environ.get('DJANGO_GCORN_LOGLEVEL', 'debug')
capture_output = os.environ.get('DJANGO_GCORN_CAPOUTPUT', False)
