import json
import subprocess

from django.core.management.base import BaseCommand, CommandError

from sites.models import Site, Scan


class Command(BaseCommand):
    help = 'Rescan all sites and store the results in the database'

    def pshtt(self, domain):
        pshtt_cmd = ['pshtt', '--json', domain]
        try:
            self.stdout.write('  Running: {}'.format(' '.join(pshtt_cmd)))
            p = subprocess.Popen(pshtt_cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True)
            stdout, stderr = p.communicate()
            # pshtt returns a list with a single item, which is a dictionary of
            # the scan results.
            pshtt_results = json.loads(stdout)[0]
        except subprocess.CalledProcessError as e:
            self.stderr.write(
                'pshtt returned a non-zero exit code %d for %s'
                % (e.returncode, domain))
        except ValueError:
            # TODO: Could be raised by json.loads if JSON is invalid
            self.stderr.write(
                'pshtt returned invalid JSON: %s'
                % (json_output,))

        return pshtt_results, stdout, stderr

    def handle(self, *args, **options):
        for site in Site.objects.all():
            self.stdout.write('Scanning: %s' % site.domain)

            # Scan the domain with pshtt
            results, stdout, stderr = self.pshtt(site.domain)

            scan = Scan(
                site=site,

                live=results['Live'],

                valid_https=results['Valid HTTPS'],
                downgrades_https=results['Downgrades HTTPS'],
                defaults_to_https=results['Defaults to HTTPS'],

                hsts=results['HSTS'],
                hsts_max_age=results['HSTS Max Age'],
                hsts_entire_domain=results['HSTS Entire Domain'],
                hsts_preload_ready=results['HSTS Preload Ready'],
                hsts_preloaded=results['HSTS Preloaded'],

                pshtt_stdout=stdout,
                pshtt_stderr=stderr,
            )
            scan.save()
