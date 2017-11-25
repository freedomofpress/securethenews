import json

from django.shortcuts import get_object_or_404, render

from .models import Site, SiteCategory


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


def leaderboard(request, slug):
    site_category = get_object_or_404(SiteCategory, slug=slug)
    sites = Site.objects.filter(site_category=site_category).all()
    return render(request, 'sites/leaderboard.html', dict(
        sites_json=json.dumps([site.to_dict() for site in sites]),
        site_category=site_category,
    ))
