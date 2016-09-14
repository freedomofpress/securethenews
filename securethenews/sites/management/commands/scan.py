import json
import subprocess

from django.core.management.base import BaseCommand, CommandError

from sites.models import Site, Scan

class Command(BaseCommand):
    help = 'Rescan all sites and store the results in the database'

    def handle(self, *args, **options):
        for site in Site.objects.all():
            self.stdout.write('Scanning: %s' % site.url)
            scan_results = None
            try:
                json_output = subprocess.check_output([
                    'pshtt', '--json', site.url])
                encoded_json_output = json_output.decode('utf-8')
                # XXX: For some reason, pshtt returns a list with a single item,
                # which is a dictionary of the scan results.
                scan_results = json.loads(encoded_json_output)[0]
            except subprocess.CalledProcessError as e:
                self.stderr.write(
                    'pshtt returned a non-zero exit code %d for %s'
                    % (e.returncode, site.url))
            except ValueError:
                # TODO: Could be raised by json.loads if JSON is invalid
                self.stderr.write(
                    'pshtt returned invalid JSON: %s'
                    % (json_output,))

            if scan_results:
                scan = Scan(
                    site=site,
                    supports_https=bool(scan_results['Valid HTTPS']),
                    enforces_https=bool(scan_results['Defaults to HTTPS']),
                )
                scan.save()
