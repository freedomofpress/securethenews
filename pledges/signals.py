# Signals are meant to be used as a last resort.  We want to send an email when
# a pledge is approved, but since this happens through wagtailmodeladmin and
# not one of the views in the pledges app, we cannot just call
# send_review_confirmation_email from the view.  Therefore, this seems like a
# reasonable use case for signals.

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Pledge
from .views import send_review_confirmation_email


@receiver(post_save, sender=Pledge)
def maybe_send_review_confirmation_email(sender, **kwargs):
    pledge = kwargs.get('instance')
    if pledge.review_status == Pledge.STATUS_APPROVED:
        send_review_confirmation_email(pledge)
