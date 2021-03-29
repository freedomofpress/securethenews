import os

from django.http import HttpResponse
from django.views.decorators.cache import never_cache


DEPLOYINFO_PATH = os.environ.get('DJANGO_VERSION_FILE', '/deploy/version')


def deploy_info_view(request):
    try:
        with open(DEPLOYINFO_PATH, 'r') as f:
            contents = f.read()
    except FileNotFoundError:
        contents = "<file not found at {}>".format(DEPLOYINFO_PATH)
    return HttpResponse(contents, content_type='text/plain')


@never_cache
def health_ok(request):
    """Lightweight health-check with a 200 response code."""
    return HttpResponse("okay")
