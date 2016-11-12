from base64 import b16encode
from os import urandom

from django.db import models


# Create your models here.
def generate_confirmation_nonce():
    # Use Base-16 to avoid potential URL encoding issues
    return b16encode(urandom(32))


class Pledge(models.Model):
    site = models.ForeignKey(
        'sites.Site',
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
