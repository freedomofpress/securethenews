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
    live = models.BooleanField()
    # These are nullable because it may not be possible to determine their
    # values (for example, if the site is down at the time of the scan).
    valid_https = models.NullBooleanField()
    default_https = models.NullBooleanField()
    enforces_https = models.NullBooleanField()
    downgrades_https = models.NullBooleanField()

    score = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return "Scan for %s on %s" % (self.site.name, self.timestamp)

    def save(self, *args, **kwargs):
        self._score()
        super(Scan, self).save(*args, **kwargs)

    def _score(self):
        """Compute a score between 0-100 for the quality of the HTTPS implementation observed by this scan."""
        # TODO: this is a very basic metric, just so we have something for
        # testing. Revisit.
        score = 0
        if self.valid_https:
            score = 20
        if self.default_https:
            score = 90
        if self.enforces_https:
            score = 100
        assert score >= 0 and score <= 100, \
            "score is not in the range 0-100: %d" % score
        self.score = score
