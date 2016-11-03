from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

import json

from .forms import PledgeForm
from .models import Site


def index(request):
    sites = Site.objects.all()
    return render(request, 'sites/index.html', dict(
        sites_json=json.dumps([site.to_dict() for site in sites]),
    ))


def site(request, slug):
    site = get_object_or_404(Site, slug=slug)
    latest_scan = site.scans.latest()
    return render(request, 'sites/site.html', dict(
        site=site,
        scan=latest_scan,
    ))


def pledge(request):
    if request.method == 'POST':
        form = PledgeForm(request.POST)
        if form.is_valid():
            form.save()
            # TODO: process data
            # TODO: set up response redirect
            return HttpResponseRedirect(reverse('sites:pledge_thanks'))
    else:
        form = PledgeForm()

    return render(request, 'sites/pledge.html', {'form': form})


def pledge_thanks(request):
    return render(request, 'sites/pledge_thanks.html')
