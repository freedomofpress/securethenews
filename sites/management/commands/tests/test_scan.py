from sites.management.commands.scan import is_onion_available
from django.test import TestCase


class TestScan(TestCase):
    def test_invalid_onion_available_over_http(self):
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
                },
                "https": {"headers": {}},
                "httpswww": {"headers": {}},
                "httpwww": {
                    "headers": {
                        "onion-location": "https://www.foobar.onion/",
                    },
                },
            }
        }
        assert not is_onion_available(http_onion_available_pshtt)

    def test_onion_available_over_https(self):
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

    def test_no_onion_available_over_https(self):
        """Simulates a HTTPS site without the Onion-Location header"""
        https_onion_not_available_pshtt = {
            "endpoints": {
                "http": {"headers": {}},
                "https": {"headers": {}},
                "httpswww": {"headers": {}},
                "httpwww": {"headers": {}},
            }
        }
        assert not is_onion_available(https_onion_not_available_pshtt)
