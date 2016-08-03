from django.db import models


class Site(models.Model):
    name = models.CharField('Name', max_length=255, unique=True)
    url = models.CharField(
        'URL',
        max_length=255,
        unique=True,
        help_text='Specify the domain name without the scheme, e.g. "example.com" instead of "https://example.com"')

    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class Scan(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='scans')
    added = models.DateTimeField(auto_now_add=True)

    # Scan results
    supports_https = models.BooleanField()
