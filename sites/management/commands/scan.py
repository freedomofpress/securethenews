import json
from lxml import etree, html
import requests
import subprocess
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import structlog

from sites.models import Site, Scan

logger = structlog.get_logger()

TIMEOUT_REQUESTS = 5


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


def is_onion_loc_in_meta_tag(url: str) -> Optional[bool]:
    """
    Make request to target URL, parse page content and see if there is a
    tag with format:

    <meta http-equiv="onion-location" content="http://myonion.onion">
    """
    try:
        r = requests.get(url, timeout=TIMEOUT_REQUESTS)
        tree = html.fromstring(r.content)
        tags = tree.xpath('//meta[@http-equiv="onion-location"]/@content')
        if len(tags) >= 1:
            return True
    except (etree.ParserError, requests.exceptions.RequestException) as e:
        # Error when requesting or parsing the page content, we log and
        # continue on.
        logger.error(e)
        return None

    return False


def is_onion_available(pshtt_results) -> Optional[bool]:
    """
    For HTTPS sites, we see if an Onion-Location is provided, indicating that
    the site is available as an onion service.
    """
    onion_available = False

    # First we see if the header is provided.
    for key in ["https", "httpswww"]:
        try:
            headers = pshtt_results["endpoints"][key]["headers"]
            if 'onion-location' in set(k.lower() for k in headers):
                onion_available = True
                return onion_available
        except KeyError:
            pass

    # If the header is not provided, it's possible the news organization
    # has included it the HTML of the page in a meta tag using the `http-equiv`
    # attribute.
    canonical_url = pshtt_results.get("Canonical URL", None)
    if not canonical_url:
        base_domain = pshtt_results.get("Base Domain", None)
        logger.error('could not find canonical URL for {}'.format(base_domain))
        return None
    elif not canonical_url.startswith("https://"):  # Skip scan if not HTTPS.
        return False
    else:
        onion_available = is_onion_loc_in_meta_tag(canonical_url)

    return onion_available


def scan(site):
    # Scan the domain with pshtt
    results, stdout, stderr = pshtt(site.domain)

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

        onion_location_header=is_onion_available(results),

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
                print(f"Scanning: {site.domain}", file=self.stdout, flush=True)
                scan(site)
