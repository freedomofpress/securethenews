import json
import subprocess

from django.core.management.base import BaseCommand, CommandError

from scans.models import Site, Scan

class Command(BaseCommand):
    help = 'Re-scans all sites that are currently being tracked'

    def handle(self, *args, **options):
        for site in Site.objects.all():
            self.stdout.write('Scanning: %s' % site.url)
            scan_results = None
            try:
                json_output = subprocess.check_output(
                    ['site-inspector', 'inspect', site.url, '-j'])
                encoded_json_output = json_output.decode('utf-8')
                scan_results = json.loads(encoded_json_output)
            except subprocess.CalledProcessError as e:
                self.stderr.write(
                    'site-inspector returned a non-zero exit code %d for %s'
                    % (e.returncode, site.url))
            except ValueError:
                # TODO: Could be raised by json.loads if site-inspector returns invalid JSON
                self.stderr.write(
                    'site-inspector returned invalid JSON: %s'
                    % (json_output,))

            if scan_results:
                scan = Scan(
                    site=site,
                    supports_https=scan_results['https'],
                    enforces_https=scan_results['enforces_https'],
                )
                scan.save()
