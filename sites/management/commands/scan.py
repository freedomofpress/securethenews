import json
import subprocess

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from sites.models import Site, Scan


def pshtt(domain):
    pshtt_cmd = ['pshtt', '--json', '--timeout', '5', domain]

    p = subprocess.Popen(
        pshtt_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True)
    stdout, stderr = p.communicate()

    # pshtt returns a list with a single item, which is a dictionary of
    # the scan results.
    pshtt_results = json.loads(stdout)[0]

    return pshtt_results, stdout, stderr


def is_onion_available(pshtt_results):
    """
    For HTTPS sites, we inspect the headers to see if the
    Onion-Location header is present, indicating that the
    site is available as an onion service.
    """
    onion_available = False

    for key in ["https", "httpswww"]:
        try:
            headers = pshtt_results["endpoints"][key]["headers"]
            if 'onion-location' in set(k.lower() for k in headers):
                onion_available = True
        except KeyError:
            pass

    return onion_available


def scan(site):
    # Scan the domain with pshtt
    results, stdout, stderr = pshtt(site.domain)

    scan = Scan(
        site=site,
        onion_available=is_onion_available(results),

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


class Command(BaseCommand):
    help = 'Rescan all sites and store the results in the database'

    def add_arguments(self, parser):
        parser.add_argument('sites', nargs='*', type=str, default='',
                            help=(
                                "Specify one or more domain names of sites"
                                " to scan. If unspecified, scan all sites."))

    def handle(self, *args, **options):
        # Support targeting a specific site to scan.
        if options['sites']:
            sites = []
            for domain_name in options['sites']:
                try:
                    site = Site.objects.get(domain=domain_name)
                    sites.append(site)
                except Site.DoesNotExist:
                    msg = "Site with domain '{}' does not exist".format(
                            domain_name)
                    raise CommandError(msg)
        else:
            sites = Site.objects.all()

        with transaction.atomic():
            for site in sites:
                self.stdout.write('Scanning: {}'.format(site.domain))
                scan(site)
