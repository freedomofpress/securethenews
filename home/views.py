import os

from django.http import HttpResponse


GITINFO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'gitinfo')


def gitinfo_view(request):
    try:
        with open(GITINFO_PATH, 'r') as f:
            contents = f.read()
    except FileNotFoundError:
        contents = "<file not found at {}>".format(GITINFO_PATH)
    return HttpResponse(contents, content_type='text/plain')
