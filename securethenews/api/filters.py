"""
Filters are used by the Django REST Framework to handle query URLs such as
?domain=bbc.co.uk.
"""
import django_filters
from sites.models import Site


class SiteFilter(django_filters.rest_framework.FilterSet):
    """
    Filter for selected fields and the date range in which a site was added
    """
    # This is nicer than the default, which only lets you input a specific
    # date.
    added_date = django_filters.DateTimeFromToRangeFilter(name='added')

    class Meta:
        model = Site
        fields = ('name', 'domain', 'slug', 'added_date')
