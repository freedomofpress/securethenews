"""
Filters are used by the Django REST Framework to handle query URLs such as
?domain=bbc.co.uk.
"""
import django_filters
from sites.models import Site, Scan


class SiteFilter(django_filters.rest_framework.FilterSet):
    """
    Filter for selected site fields and the date range in which a site was added
    """
    # This is nicer than the default, which only lets you input a specific
    # date.
    added_range = django_filters.DateTimeFromToRangeFilter(name='added')

    class Meta:
        model = Site
        fields = ('name', 'domain', 'slug', 'added_range')


class ScanFilter(django_filters.rest_framework.FilterSet):
    """
    Filter for selected scan fields and the date range in which a scan was
    performed, as well as the score range among a list of scans
    """
    timestamp_range = django_filters.DateTimeFromToRangeFilter(
        name='timestamp')
    score_range = django_filters.RangeFilter(name='score')

    class Meta:
        model = Scan
        fields = ('timestamp_range', 'live', 'valid_https',
                  'defaults_to_https', 'score_range')
