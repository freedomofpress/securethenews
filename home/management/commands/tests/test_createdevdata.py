import os

from django.core import management
from django.test import TestCase


class CreateDevDataSmokeTest(TestCase):

    def test_createdevdata_works(self):
        """The createdevdata management command should run successfully,
        without raising any exceptions."""
        # Write stdout to /dev/null so as not to clutter the output
        # from the tests.
        with open(os.devnull, 'w') as devnull:
            management.call_command('createdevdata', stdout=devnull)
