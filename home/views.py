import os

from django.http import HttpResponse


DEPLOYINFO_PATH = os.environ.get('DJANGO_VERSION_FILE', '/deploy/version')


def deploy_info_view(request):
    try:
        with open(DEPLOYINFO_PATH, 'r') as f:
            contents = f.read()
    except FileNotFoundError:
        contents = "<file not found at {}>".format(DEPLOYINFO_PATH)
    return HttpResponse(contents, content_type='text/plain')
