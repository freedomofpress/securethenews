import requests
from unittest import mock

from sites.management.commands.scan import (is_onion_available,
                                            is_onion_loc_in_meta_tag)
from django.test import TestCase


META_TAG = '<meta http-equiv="onion-location" content="http://myonion.onion">'


class TestScan(TestCase):
    @mock.patch('sites.management.commands.scan.is_onion_loc_in_meta_tag',
                return_value=False)
    def test_invalid_onion_available_over_http(self, mock_onion):
        """Simulates a HTTP site with the onion location header,
        which is invalid: Onion-Location is ignored if not served
        over HTTPS
        """
        http_onion_available_pshtt = {
            "endpoints": {
                "http": {
                    "headers": {
                        "onion-location": "https://www.foobar.onion/",
                    },
                    "url": "http://example.com"
                },
                "https": {"headers": {}, "url": "https://example.com"},
                "httpswww": {"headers": {}, "url": "https://www.example.com"},
                "httpwww": {
                    "headers": {
                        "onion-location": "https://www.foobar.onion/",
                        "url": "http://www.example.com",
                    },
                },
            }
        }
        assert is_onion_available(http_onion_available_pshtt) is False

    @mock.patch('sites.management.commands.scan.is_onion_loc_in_meta_tag',
                return_value=False)
    def test_onion_available_over_https(self, mock_onion):
        """Simulates a HTTPS site with the onion location header"""
        https_onion_available_pshtt = {
            "endpoints": {
                "http": {
                    "headers": {
                        "onion-location": "https://www.foobar.onion/",
                    },
                },
                "https": {
                    "headers": {
                        "onion-location": "https://www.foobar.onion/",
                    },
                },
                "httpswww": {
                    "headers": {
                        "onion-location": "https://www.foobar.onion/",
                    },
                },
                "httpwww": {
                    "headers": {
                        "onion-location": "https://www.foobar.onion/",
                    },
                },
            }
        }
        assert is_onion_available(https_onion_available_pshtt)

    @mock.patch('sites.management.commands.scan.is_onion_loc_in_meta_tag',
                return_value=False)
    def test_no_onion_available_over_https(self, mock_onion):
        """
        Simulates a HTTPS site without the Onion-Location either in the
        header or the meta tag
        """
        https_onion_not_available_pshtt = {
            "endpoints": {
                "http": {"headers": {}, "url": "http://example.com"},
                "https": {"headers": {}, "url": "https://example.com"},
                "httpswww": {"headers": {}, "url": "https://www.example.com"},
                "httpwww": {"headers": {}, "url": "http://www.example.com"},
            }
        }
        assert is_onion_available(https_onion_not_available_pshtt) is False

    @mock.patch('sites.management.commands.scan.is_onion_loc_in_meta_tag',
                return_value=True)
    def test_onion_available_over_https_meta_tag(self, mock_onion):
        """
        Simulates a HTTPS site with the Onion-Location header provided
        only in the meta tag
        """
        https_onion_not_available_in_header_pshtt = {
            "endpoints": {
                "http": {"headers": {}, "url": "http://example.com"},
                "https": {"headers": {}, "url": "https://example.com"},
                "httpswww": {"headers": {}, "url": "https://www.example.com"},
                "httpwww": {"headers": {}, "url": "http://www.example.com"},
            }
        }
        assert is_onion_available(https_onion_not_available_in_header_pshtt)

    def test_is_onion_loc_in_meta_tag_found(self):
        """
        Check we return True if the onion-location meta tag is found.
        """
        url = "example.com"

        resp = mock.MagicMock()
        type(resp).content = mock.PropertyMock(return_value=META_TAG)

        with mock.patch('requests.get', return_value=resp):
            assert is_onion_loc_in_meta_tag(url)

    def test_is_onion_loc_in_meta_tag_not_found(self):
        """
        Check we return False if no onion-location meta tag is found.
        """
        url = "example.com"

        resp = mock.MagicMock()
        type(resp).content = mock.PropertyMock(return_value="<html></html>")

        with mock.patch('requests.get', return_value=resp):
            assert is_onion_loc_in_meta_tag(url) is False

    def test_is_onion_loc_in_meta_tag_error(self):
        """
        Check we return None if the scan fails.
        """
        url = "example.com"

        resp = mock.MagicMock()
        type(resp).content = mock.PropertyMock(
            side_effect=requests.exceptions.RequestException()
        )

        with mock.patch('requests.get', return_value=resp):
            assert is_onion_loc_in_meta_tag(url) is None
