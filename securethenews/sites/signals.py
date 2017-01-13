from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from wagtail.contrib.wagtailfrontendcache.utils import purge_url_from_cache

from sites.models import Scan


@receiver(post_save, sender=Scan)
def invalidate_frontend_cache_for_site(sender, instance, **kwargs):
    # Purge site-specific score breakdown page
    purge_url_from_cache(reverse(instance.site))

    # Purge the leaderboard
    purge_url_from_cache(reverse('sites:index'))

    # Purge the home page because it displays a subset of the leaderboard, as well as some summary statistics.
    purge_url_from_cache('/')
