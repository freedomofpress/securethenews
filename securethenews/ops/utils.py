# Yanked out upstream CloudflareBackend from master wagtail branch
#   commit: a5b544631bbde21b28ff749dcd53d35e5f5bf64d
#   file: wagtail/contrib/wagtailfrontendcache/backends.py
#
# This was necessary because the tagged v1.7 doesn't support the latest
# API for cloudflare
import logging
import requests
from wagtail.contrib.wagtailfrontendcache.backends import BaseBackend

logger = logging.getLogger('wagtail.frontendcache')


class CloudflareBackend(BaseBackend):
    def __init__(self, params):
        self.cloudflare_email = params.pop('EMAIL')
        self.cloudflare_token = params.pop('TOKEN')
        self.cloudflare_zoneid = params.pop('ZONEID')

    def purge(self, url):
        try:
            purge_url = 'https://api.cloudflare.com/client/v4/zones/{0}/purge_cache'.format(self.cloudflare_zoneid)

            headers = {
                "X-Auth-Email": self.cloudflare_email,
                "X-Auth-Key": self.cloudflare_token,
                "Content-Type": "application/json",
            }

            data = {"files": [url]}

            response = requests.delete(
                purge_url,
                json=data,
                headers=headers,
            )

            try:
                response_json = response.json()
            except ValueError:
                if response.status_code != 200:
                    response.raise_for_status()
                else:
                    logger.error("Couldn't purge '%s' from Cloudflare. Unexpected JSON parse error.", url)

        except requests.exceptions.HTTPError as e:
            logger.error("Couldn't purge '%s' from Cloudflare. HTTPError: %d %s", url, e.response.status_code, e.message)
            return
        except requests.exceptions.InvalidURL as e:
            logger.error("Couldn't purge '%s' from Cloudflare. URLError: %s", url, e.message)
            return

        if response_json['success'] is False:
            error_messages = ', '.join([err['message'] for err in response_json['errors']])
            logger.error("Couldn't purge '%s' from Cloudflare. Cloudflare errors '%s'", url, error_messages)
        else:
            logger.info("Successfully purged '%s' from Cloudflare.", url)
        return
