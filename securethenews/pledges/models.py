from base64 import b16encode
from os import urandom
from urllib.parse import urlencode

from django.core.mail import mail_admins, send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string

from sites.models import Site

# Create your models here.
def generate_confirmation_nonce():
    # Use Base-16 to avoid potential URL encoding issues
    return b16encode(urandom(32))

class Pledge(models.Model):
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name='pledges'
    )
    url = models.URLField()
    contact_email = models.EmailField()

    confirmed = models.BooleanField(default=False, editable=False)
    confirmation_nonce = models.CharField(
        max_length=255,
        default=generate_confirmation_nonce,
        editable=False
    )

    STATUS_NEEDS_REVIEW = 'N'
    STATUS_APPROVED = 'A'
    STATUS_REJECTED = 'R'
    STATUS_CHOICES = (
        (STATUS_NEEDS_REVIEW, 'Needs Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )
    review_status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=STATUS_NEEDS_REVIEW
    )

    submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Pledge: {}".format(self.site.name)

    # TODO Email handling in the model is nice in some ways, but weird in
    # others. It feels kind of like a violation of MVC design. Consider
    # refactoring.

    def send_confirmation_email(self, request):
        assert not self.confirmed, "{} is already confirmed"

        subject = "Confirm your pledge to secure your site"

        confirmation_link = request.build_absolute_uri("{}?{}".format(
            reverse('pledges:confirm', kwargs={'pk': self.pk}),
            urlencode({'nonce': self.confirmation_nonce})
        ))

        message = render_to_string('pledges/emails/confirmation.txt', {
            'confirmation_link': confirmation_link
        })

        send_mail(
            subject=subject,
            message=message,
            from_email='contact@securethe.news',
            recipient_list=[self.contact_email,]
        )

    def send_admin_notification_email(self, request):
        """Notify the admins that a submitted pledge has been confirmed and is ready for review."""
        subject = 'Pledge Ready for Review: {}'.format(self.site.name)

        # Get the wagtailmodeladmin PledgeAdmin so we can derive the edit
        # url for the newly submitted pledge.
        # TODO: we have to import this here to avoid circular imports, which is
        # gross. Refactor?
        from .wagtail_hooks import PledgeAdmin
        pledge_admin = PledgeAdmin()
        body = render_to_string('pledges/emails/admin_notification.txt', {
            'site': self.site,
            'moderation_link': request.build_absolute_uri(
                pledge_admin.url_helper.get_action_url('edit', self.pk)
            ),
        })

        mail_admins(subject, body)

    def send_review_confirmation_email(self):
        subject = 'Secure the News Pledge Review: {}'.format(
            self.get_review_status_display())

        message = render_to_string('pledges/emails/reviewed.txt',
            { 'pledge': self }
        )

        send_mail(
            subject=subject,
            message=message,
            from_email='contact@securethe.news',
            recipient_list=[self.contact_email,]
        )

    def save(self, *args, **kwargs):
        if self.review_status in (self.STATUS_APPROVED, self.STATUS_REJECTED):
            self.send_review_confirmation_email()
        super(Pledge, self).save(*args, **kwargs)
