import argparse
import csv
from os.path import abspath

from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.exceptions import ValidationError

from sites.models import Site


class Command(BaseCommand):
    help = 'Load sites from CSV'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            'csvfile',
            type=argparse.FileType('r'),
            help='Path to .csv file containing site names and domain names')

    def handle(self, *args, **options):
        csvfile = options['csvfile']
        reader = csv.DictReader(csvfile)

        # Wrap in a transaction so if creating any site fails, the database
        # will automatically rollback.
        with transaction.atomic():
            num_rows = 0
            for row in reader:
                new_site = Site(
                    name=row['Organization Name'],
                    domain=row['Domain Name']
                )
                try:
                    new_site.validate_unique()
                except ValidationError:
                    continue

                new_site.save()
                num_rows += 1

            print('Added {} new site(s) from {}'.format(
                num_rows, abspath(csvfile.name)))
