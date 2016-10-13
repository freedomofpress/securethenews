from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import json

from .models import Site


def index(request):
    sites = Site.objects.all()
    sites_dicts = [s.to_dict() for s in sites]
    return render(request, 'sites/index.html', dict(
        sites=sites,
        sites_json=json.dumps(sites_dicts),
    ))


def site(request, slug):
    site = get_object_or_404(Site, slug=slug)
    return render(request, 'sites/site.html', dict(
        site=site,
    ))
