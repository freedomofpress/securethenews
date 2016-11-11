from base64 import b16encode
from os import urandom
from urllib.parse import urlencode

from django.core.mail import mail_admins, send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string
from django.utils.text import slugify


class Site(models.Model):
    name = models.CharField('Name', max_length=255, unique=True)
    slug = models.SlugField('Slug', unique=True, editable=False)

    domain = models.CharField(
        'Domain Name',
        max_length=255,
        unique=True,
        help_text='Specify the domain name without the scheme, e.g. "example.com" instead of "https://example.com"')

    added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Site, self).save(*args, **kwargs)

    def to_dict(self):
        """Generate a JSON-serializable dict of this object's attributes,
        including the results of the most recent scan."""
        # TODO optimize this (denormalize latest scan into Site?)
        return dict(
            name=self.name,
            slug=self.slug,
            domain=self.domain,
            **self.scans.latest().to_dict()
        )

class Scan(models.Model):
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name='scans')

    timestamp = models.DateTimeField(auto_now_add=True)

    # Scan results
    # TODO: If a site isn't live, there may not be much of a point storing the
    # scan. This requirement also increases the complexity of the data model
    # since it means the attributes of the scan results must be nullable.
    live = models.BooleanField()

    # These are nullable because it may not be possible to determine their
    # values (for example, if the site is down at the time of the scan).
    valid_https = models.NullBooleanField()
    downgrades_https = models.NullBooleanField()
    defaults_to_https = models.NullBooleanField()

    hsts = models.NullBooleanField()
    hsts_max_age = models.IntegerField(null=True)
    hsts_entire_domain = models.NullBooleanField()
    hsts_preload_ready = models.NullBooleanField()
    hsts_preloaded = models.NullBooleanField()

    score = models.IntegerField(default=0, editable=False)

    # To aid debugging, we store the full stdout and stderr from pshtt.
    pshtt_stdout = models.TextField()
    pshtt_stderr = models.TextField()

    class Meta:
        get_latest_by = 'timestamp'

    def __str__(self):
        return "{} from {:%Y-%m-%d %H:%M}".format(self.site.name,
                                                  self.timestamp)

    def save(self, *args, **kwargs):
        self._score()
        super(Scan, self).save(*args, **kwargs)

    def _score(self):
        """Compute a score between 0-100 for the quality of the HTTPS implementation observed by this scan."""
        # TODO: this is a very basic metric, just so we have something for
        # testing. Revisit.
        score = 0
        if self.valid_https:
            if self.downgrades_https:
                score = 30
            else:
                score = 50

            if self.defaults_to_https:
                score = 70

                if self.hsts:
                    score += 5

                # HSTS max-age is specified in seconds
                eighteen_weeks = 18*7*24*60*60
                if self.hsts_max_age and self.hsts_max_age >= eighteen_weeks:
                    score += 5

                if self.hsts_entire_domain:
                    score += 10
                if self.hsts_preload_ready:
                    score += 5
                if self.hsts_preloaded:
                    score += 5

        assert 0 <= score <= 100, \
            "score must be between 0 and 100 (inclusive), is: {}".format(score)
        self.score = score

    def to_dict(self):
        return dict(
            live=self.live,
            valid_https=self.valid_https,
            downgrades_https=self.downgrades_https,
            defaults_to_https=self.defaults_to_https,
            hsts=self.hsts,
            hsts_max_age=self.hsts_max_age,
            hsts_entire_domain=self.hsts_entire_domain,
            hsts_preload_ready=self.hsts_preload_ready,
            hsts_preloaded=self.hsts_preloaded,
            score=self.score
        )

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

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Pledge: {}".format(self.site.name)

    # TODO Email handling in the model is nice in some ways, but weird in
    # others. It feels kind of like a violation of MVC design. Consider
    # refactoring.

    def send_confirmation_email(self, request):
        assert not self.confirmed, "{} is already confirmed"

        subject = "Confirm your pledge to secure your site"

        confirmation_link = request.build_absolute_uri("{}?{}".format(
            reverse('sites:confirm_pledge', kwargs={'pk': self.pk}),
            urlencode({'nonce': self.confirmation_nonce})
        ))

        message = render_to_string('sites/pledge_confirmation_email.txt', {
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
        body = render_to_string('sites/pledge_admin_notification_email.txt', {
            'site': self.site,
            'moderation_link': request.build_absolute_uri(
                pledge_admin.url_helper.get_action_url('edit', self.pk)
            ),
        })

        mail_admins(subject, body)
