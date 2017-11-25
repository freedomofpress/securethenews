from django.forms import ValidationError
from django.test import TestCase

from sites.models import Site, Scan, SiteCategory


class TestSite(TestCase):

    def setUp(self):
        self.site = Site.objects.create(name='Test Site', domain='test.com')

    def test_site_name_unique(self):
        """Each Site should have a unique name."""
        with self.assertRaises(ValidationError):
            dupe = Site.objects.create(  # noqa: F841
                name=self.site.name, domain='nottest.com')

    def test_site_domain_unique(self):
        """Each Site should have a unique domain."""
        with self.assertRaises(ValidationError):
            dupe = Site.objects.create(  # noqa: F841
                name='Not Test Site', domain=self.site.domain)

    def test_site_slug_unique(self):
        """Each Site should have a unique slug."""
        with self.assertRaises(ValidationError) as cm:
            # Slugification strips trailing whitespace, so adding a space to
            # the end of an existing site's name is one way to synthesize a
            # Site with a unique name but a non-unique slug.
            dupe = Site.objects.create(  # noqa: F841
                name=self.site.name + ' ', domain='nottest.com')

        self.assertIn(
            'Site with this Slug already exists.',
            cm.exception.messages)

    def test_unicode_aware_slugs(self):
        """Non-ASCII characters in a Site's name should be
        included without modification in the auto-generated slug."""
        site = Site.objects.create(name='El País', domain='elpais.es')
        self.assertIn('í', site.slug)

    def test_unicode_aware_slugs_can_be_modified(self):
        """Non-ASCII characters in a Site's name will be revalidated
        on model save, so let's make a change to an unrelated field
        and confirm no exceptions are raised."""
        site = Site.objects.create(name='El País', domain='elpais.es')
        # Discovered a 500 via save operation, see #130.
        site.domain = 'elpais.com'
        # Will raise Exception if slug doesn't support Unicode.
        site.save()
        self.assertIn('í', site.slug)

    def test_site_without_pledge(self):
        """Site.pledge should return None if there are no approved
        pledges for the Site."""
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
        """If a Site hasn't been scanned yet, it shouldn't be available through
        the ScannedSitesManager."""
        self.assertNotIn(self.site, Site.scanned.all())

    def test_scanned_sites_available(self):
        """Once a Site has been scanned, it should be available through the
        ScannedSitesManager."""
        scan = Scan.objects.create(site=self.site, live=False)  # noqa: F841
        self.assertIn(self.site, Site.scanned.all())


class TestSiteCategory(TestCase):

    def setUp(self):
        self.site = Site.objects.create(name='Test Site', domain='test.com')

    def test_duplicate_categories_cannot_be_created(self):
        SiteCategory.objects.create(name='test value')

        # Try to insert a duplicate value
        with self.assertRaises(ValidationError):
            SiteCategory.objects.create(name='test value')

    def test_saving_category_creates_slug(self):
        site_category = SiteCategory.objects.create(name='test value')
        site_category.save()
        self.assertEqual(site_category.slug, 'test-value')
