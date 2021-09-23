import os

from django.http import HttpResponse
from django.views.decorators.cache import never_cache


VERSION_INFO_SHORT_PATH = os.environ.get(
    "DJANGO_SHORT_VERSION_FILE", "/deploy/version-short.txt"
)
VERSION_INFO_FULL_PATH = os.environ.get(
    "DJANGO_FULL_VERSION_FILE", "/deploy/version-full.txt"
)


def read_version_info_file(p):
    try:
        with open(p, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"<file not found at {p}>"


def deploy_info_view(request):
    version_full_text = read_version_info_file(VERSION_INFO_FULL_PATH)
    return HttpResponse(version_full_text, content_type="text/plain")


@never_cache
def health_ok(request):
    """Lightweight health-check with a 200 response code."""
    return HttpResponse("okay")


def health_version(request):
    """Also a health check, but returns the commit short-hash."""
    version_short_text = read_version_info_file(VERSION_INFO_SHORT_PATH)
    return HttpResponse(version_short_text)
