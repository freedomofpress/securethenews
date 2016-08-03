from django.core.management.base import BaseCommand, CommandError

from scans.models import Site, Scan

class Command(BaseCommand):
    help = 'Re-scans all sites that are currently being tracked'

    def handle(self, *args, **options):
        sites = Site.objects.all()
        site_urls = [site.url for site in sites]
        for site_url in site_urls:
            self.stdout.write('Scanning: %s' % site_url)
            # ...?
