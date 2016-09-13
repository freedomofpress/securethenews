from django.db import models
from django.utils.text import slugify


class Site(models.Model):
    name = models.CharField('Name', max_length=255, unique=True)
    slug = models.SlugField('Slug', unique=True, editable=False)
    url = models.CharField(
        'URL',
        max_length=255,
        unique=True,
        help_text='Specify the domain name without the scheme, e.g. "example.com" instead of "https://example.com"')

    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Site, self).save(*args, **kwargs)

class Scan(models.Model):
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name='sites')
    timestamp = models.DateTimeField(auto_now_add=True)

    # Scan results
    supports_https = models.BooleanField()
    enforces_https = models.BooleanField()

    def __str__(self):
        return "Scan for %s on %s" % (self.site.name, self.timestamp)
