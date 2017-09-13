from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import mail_admins, send_mail
from django.core.exceptions import SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.crypto import constant_time_compare

from .forms import PledgeForm
from .models import Pledge
from .wagtail_hooks import PledgeAdmin


def pledge(request):
    if request.method == 'POST':
        form = PledgeForm(request.POST)
        if form.is_valid():
            new_pledge = form.save()
            send_confirmation_email(request, new_pledge)
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
        send_admin_notification_email(request, pledge)

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


def send_confirmation_email(request, pledge):
    assert not pledge.confirmed, "{} is already confirmed"

    subject = "Confirm your pledge to secure your site"

    confirmation_link = request.build_absolute_uri("{}?{}".format(
        reverse('pledges:confirm', kwargs={'pk': pledge.pk}),
        urlencode({'nonce': pledge.confirmation_nonce})
    ))

    message = render_to_string('pledges/emails/confirmation.txt', {
        'confirmation_link': confirmation_link
    })

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[pledge.contact_email,]
    )

def send_admin_notification_email(request, pledge):
    """Notify the admins that a submitted pledge has been confirmed and is ready for review."""
    subject = 'Pledge Ready for Review: {}'.format(pledge.site.name)

    # Get the wagtailmodeladmin PledgeAdmin so we can derive the edit
    # url for the newly submitted pledge.
    pledge_admin = PledgeAdmin()

    body = render_to_string('pledges/emails/admin_notification.txt', {
        'site': pledge.site,
        'moderation_link': request.build_absolute_uri(
            pledge_admin.url_helper.get_action_url('edit', pledge.pk)
        ),
    })

    mail_admins(subject, body)

def send_review_confirmation_email(pledge):
    subject = 'Secure the News Pledge Review: {}'.format(
        pledge.get_review_status_display())

    message = render_to_string('pledges/emails/reviewed.txt',
        { 'pledge': pledge }
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[pledge.contact_email,]
    )
