"""
Tests basic API operations against simple test data.
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from sites.models import Site, Scan
from urllib.parse import urljoin

urlroot = reverse('api-root-v1')


def create_site():
    """
    Make an example site + scans
    """
    site = Site.objects.create(
        name='Secure the News', domain='securethe.news')
    Scan.objects.create(site=site, live=True, defaults_to_https=False)
    Scan.objects.create(site=site, live=True, defaults_to_https=True)


class APIDirectoryTests(APITestCase):
    def test_get_directory(self):
        """
        API root should return a directory of API operations
        """
        response = self.client.get(urlroot, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # We're deliberately just testing one key so the directory can be
        # modified without breaking tests
        self.assertIn('sites', response.data)


class APISiteTests(APITestCase):

    def setUp(self):
        create_site()

    def test_get_sites(self):
        """
        <api root>/sites should list sites/scan that have been created
        """
        url = urljoin(urlroot, 'sites/')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        sitedata = response.data['results'][0]
        self.assertEqual(sitedata['name'], 'Secure the News')
        self.assertIn('latest_scan', sitedata)
        self.assertIn('all_scans', sitedata)
        self.assertTrue(sitedata['latest_scan']['live'])


class APISiteDetailTests(APITestCase):
    def setUp(self):
        create_site()

    def test_get_site(self):
        """
        <api root>/sites/securethe.news should return created site details
        """
        url = urljoin(urlroot, 'sites/securethe.news/')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Secure the News')


class APISiteScansTests(APITestCase):
    def setUp(self):
        create_site()

    def test_get_site_scans(self):
        """
        <api root>/sites/securethe.news/scans should return three scans
        (first scan is done on creation)
        """
        url = urljoin(urlroot, 'sites/securethe.news/scans/')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The API itself should return a result count
        self.assertEqual(response.data['count'], 3)
        self.assertTrue(response.data['results'][0]['live'])


class APIPermissionTests(APITestCase):
    def setUp(self):
        create_site()

    def test_forbidden_actions(self):
        """
        <api root>/sites/ should not permit POST, PUT or DELETE operations
        """
        url = urljoin(urlroot, 'sites/securethe.news/')
        response1 = self.client.post(
            url, json={'name': 'Insecure the News?',
                       'domain': 'insecurethe.news'})
        self.assertEqual(response1.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

        response2 = self.client.delete(url)
        self.assertEqual(response2.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

        url = urljoin(urlroot, 'sites/insecurethe.news/')
        response3 = self.client.put(
            url, json={'name': 'Insecure the News?',
                       'domain': 'insecurethe.news'})
        self.assertEqual(response3.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
