from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.crypto import constant_time_compare

from .forms import PledgeForm
from .models import Pledge

def pledge(request):
    if request.method == 'POST':
        form = PledgeForm(request.POST)
        if form.is_valid():
            new_pledge = form.save()
            new_pledge.send_confirmation_email(request)
            return HttpResponseRedirect(reverse('pledges:thanks'))
    else:
        form = PledgeForm()

    return render(request, 'pledges/pledge.html', {'form': form})


def thanks(request):
    return render(request, 'pledges/thanks.html')


def confirm(request, pk):
    pledge = get_object_or_404(Pledge, pk=pk)

    # If the pledge has already been confirmed, redirect to confirmation page.
    if pledge.confirmed:
        return HttpResponseRedirect(reverse('pledges:confirmed', kwargs={
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

        return HttpResponseRedirect(reverse('pledges:confirmed', kwargs={
            'pk': pledge.pk
        }))

    nonce = request.GET.get('nonce')
    if not nonce:
        return HttpResponseBadRequest()

    return render(request, 'pledges/confirm.html', {
        'pledge': pledge,
        'nonce': nonce,
    })


def confirmed(request, pk):
    pledge = get_object_or_404(Pledge, pk=pk)
    return render(request, 'pledges/confirmed.html', {'pledge': pledge})
