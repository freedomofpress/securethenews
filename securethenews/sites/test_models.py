from django.forms import ValidationError
from django.test import TestCase

from sites.models import Site, Scan


class TestSite(TestCase):

    def setUp(self):
        self.site = Site.objects.create(name='Test Site', domain='test.com')

    def test_site_name_unique(self):
        """Each Site should have a unique name."""
        with self.assertRaises(ValidationError):
            dupe = Site.objects.create(
                name=self.site.name, domain='nottest.com')

    def test_site_domain_unique(self):
        """Each Site should have a unique domain."""
        with self.assertRaises(ValidationError):
            dupe = Site.objects.create(
                name='Not Test Site', domain=self.site.domain)

    def test_site_slug_unique(self):
        """Each Site should have a unique slug."""
        with self.assertRaises(ValidationError) as cm:
            # Slugification strips trailing whitespace, so adding a space to the
            # end of an existing site's name is one way to synthesize a Site
            # with a unique name but a non-unique slug.
            dupe = Site.objects.create(
                name=self.site.name + ' ', domain='nottest.com')

        self.assertIn(
            'Site with this Slug already exists.',
            cm.exception.messages)

    def test_unicode_aware_slugs(self):
        """Non-ASCII characters in a Site's name should be included without modification in the auto-generated slug."""
        site = Site.objects.create(name='El País', domain='elpais.es')
        self.assertIn('í', site.slug)

    def test_site_without_pledge(self):
        """Site.pledge should return None if there are no approved pledges for the Site."""
        self.assertIsNone(self.site.pledge)


class TestScan(TestCase):

    def setUp(self):
        self.site = Site.objects.create(name='Test Site', domain='test.com')

    def test_score_computed_on_save(self):
        """A Site's score should be automatically computed on save."""
        # Set scan attributes such that the score will be greater than 0.
        scan = Scan(site=self.site, live=True, valid_https=True)
        self.assertEqual(scan.score, 0)
        scan.save()
        self.assertGreater(scan.score, 0)


class TestScannedSitesManager(TestCase):

    def setUp(self):
        self.site = Site.objects.create(name='Test Site', domain='test.com')

    def test_unscanned_sites_unavailable(self):
        """If a Site hasn't been scanned yet, it shouldn't be available through the ScannedSitesManager."""
        self.assertNotIn(self.site, Site.scanned.all())

    def test_scanned_sites_available(self):
        """Once a Site has been scanned, it should be available through the ScannedSitesManager."""
        scan = Scan.objects.create(site=self.site, live=False)
        self.assertIn(self.site, Site.scanned.all())
