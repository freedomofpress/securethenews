from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect,
    HttpResponseBadRequest)
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.crypto import constant_time_compare

import json

from .forms import PledgeForm
from .models import Site, Pledge


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
            new_pledge = form.save()
            new_pledge.send_confirmation_email(request)
            return HttpResponseRedirect(reverse('sites:pledge_thanks'))
    else:
        form = PledgeForm()

    return render(request, 'sites/pledge.html', {'form': form})


def pledge_thanks(request):
    return render(request, 'sites/pledge_thanks.html')


def confirm_pledge(request, pk):
    pledge = get_object_or_404(Pledge, pk=pk)

    # If the pledge has already been confirmed, redirect to confirmation page.
    if pledge.confirmed:
        return HttpResponseRedirect(reverse('sites:pledge_confirmed', kwargs={
            'pk': pledge.pk
        }))

    if request.method == 'POST':
        nonce = request.POST.get('nonce')
        if not constant_time_compare(pledge.confirmation_nonce, nonce):
            raise SuspiciousOperation(
                "Received pledge with invalid nonce (pk={}, nonce={})".format(
                    pledge.pk, nonce))

        pledge.confirmed = True
        pledge.save()
        pledge.send_admin_notification_email(request)

        return HttpResponseRedirect(reverse('sites:pledge_confirmed', kwargs={
            'pk': pledge.pk
        }))

    nonce = request.GET.get('nonce')
    if not nonce:
        return HttpResponseBadRequest()

    return render(request, 'sites/confirm_pledge.html', {
        'pledge': pledge,
        'nonce': nonce,
    })


def pledge_confirmed(request, pk):
    pledge = get_object_or_404(Pledge, pk=pk)
    return render(request, 'sites/pledge_confirmed.html', {'pledge': pledge})
