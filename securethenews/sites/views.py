import json

from django.shortcuts import get_object_or_404, render

from .models import Site


def index(request):
    sites = Site.scanned.all()
    return render(request, 'sites/index.html', dict(
        sites_json=json.dumps([site.to_dict() for site in sites]),
    ))


def site(request, slug):
    site = get_object_or_404(Site.scanned, slug=slug)
    latest_scan = site.scans.latest()
    return render(request, 'sites/site.html', dict(
        site=site,
        scan=latest_scan,
    ))
