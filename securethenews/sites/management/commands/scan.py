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

        return dict(results=pshtt_results, stdout=stdout, stderr=stderr)

    def curl(self, domain):
        endpoints = [
            ('http', ''),
            ('http', 'www'),
            ('https', ''),
            ('https', 'www'),
        ]
        curl_results = {}
        for endpoint in endpoints:
            url = '{}://{}{}/'.format(endpoint[0],
                                      endpoint[1] + '.' if endpoint[1] else '',
                                      domain)

            # curl flags explanation:
            #
            # -v gives verbose output, including request and response headers.
            #
            # -m 10 limits curl's total runtime to minimize time wasted due to
            # eventual connection failures.
            #
            # --compressed helps an edge case where a server unexpectedly
            # returns compressed data (Content-Encoding: gzip). I observed this
            # issue intermittently on http://www.nydailynews.com. When it
            # happened, curl's stdout would include the compressed data, which
            # was binary data and thus would trigger a UnicodeDecodeError. This
            # flag ensures curl will decompress the data before returning it.
            curl_cmd = ['curl', '-v', '-m', '10', '--compressed', url]

            self.stdout.write('  Running: {}'.format(' '.join(curl_cmd)))
            p = subprocess.Popen(curl_cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True)
            stdout, _ = p.communicate()
            curl_results[endpoint] = stdout

        return curl_results

    def handle(self, *args, **options):
        for site in Site.objects.all():
            self.stdout.write('Scanning: %s' % site.domain)

            # Scan the domain with pshtt
            pshtt = self.pshtt(site.domain)

            # curl the domain's four endpoints to collect data in case we need # to debug the results from pshtt
            curl = self.curl(site.domain)

            scan = Scan(
                site=site,
                live=pshtt['results']['Live'],
                valid_https=pshtt['results']['Valid HTTPS'],
                default_https=pshtt['results']['Defaults to HTTPS'],
                enforces_https=pshtt['results']['Strictly Forces HTTPS'],
                downgrades_https=pshtt['results']['Downgrades HTTPS'],
                pshtt_stdout=pshtt['stdout'],
                pshtt_stderr=pshtt['stderr'],
                curl_http=curl[('http', '')],
                curl_http_www=curl[('http', 'www')],
                curl_https=curl[('https', '')],
                curl_https_www=curl[('https', 'www')],
            )
            scan.save()
