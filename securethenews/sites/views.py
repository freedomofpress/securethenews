from django.core.mail import mail_admins
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

import json

from .forms import PledgeForm
from .models import Site
from .wagtail_hooks import PledgeAdmin


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

PLEDGE_SUBMITTED_ADMIN_EMAIL = """
A new pledge has been submitted for {}.

Moderation link: {}
"""

def pledge(request):
    if request.method == 'POST':
        form = PledgeForm(request.POST)
        if form.is_valid():
            new_pledge = form.save()

            # Get the wagtailmodeladmin PledgeAdmin so we can derive the edit
            # url for the newly submitted pledge.
            pledge_admin = PledgeAdmin()

            mail_admins(
                subject='New Pledge: {}'.format(form.cleaned_data['site'].name),
                message=PLEDGE_SUBMITTED_ADMIN_EMAIL.format(
                    form.cleaned_data['site'].name,
                    request.build_absolute_uri(
                        pledge_admin.url_helper.get_action_url(
                            'edit',
                            new_pledge.pk
                        )
                    )
                )
            )

            return HttpResponseRedirect(reverse('sites:pledge_thanks'))
    else:
        form = PledgeForm()

    return render(request, 'sites/pledge.html', {'form': form})


def pledge_thanks(request):
    return render(request, 'sites/pledge_thanks.html')
