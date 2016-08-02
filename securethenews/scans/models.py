from django.db import models


class Site(models.Model):
    url = models.URLField(unique=True)
    added = models.DateTimeField(auto_now_add=True)
    

class Scan(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='scans')
    timestamp = models.DateTimeField()

    # Scan results
    supports_https = models.BooleanField()
