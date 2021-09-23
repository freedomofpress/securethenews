from django.test import TestCase, override_settings
from wagtail.core.models import Site, Page

from home.models import HomePage


class HealthCheckTestCase(TestCase):
    def test_health_check_url_returns_200_status(self):
        self.response = self.client.get("/health/ok/")
        self.assertEqual(self.response.status_code, 200)

    def test_version_info_url_returns_200_status(self):
        self.response = self.client.get("/health/version/")
        self.assertEqual(self.response.status_code, 200)


class HomePageTestCase(TestCase):
    def setUp(self):
        site = Site.objects.get()
        page = Page.get_first_root_node()
        home = HomePage(
            title="Test Title",
            main_title="Test 1",
            sub_title="Test 2",
            why_header="Test 3",
            how_header="Test 4",
            why_body="Test 5",
            how_body="Test 6",
        )
        self.home_page = page.add_child(instance=home)

        site.root_page = home
        site.save()

    @override_settings(ANALYTICS_ENABLED=False)
    def test_analytics_settings_are_in_page_context(self):
        response = self.client.get(self.home_page.url)
        self.assertIn("django_settings", response.context)
        self.assertEqual(
            response.context["django_settings"]["ANALYTICS_ENABLED"],
            False,
        )
