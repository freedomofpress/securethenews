import django_filters
from sites.models import Site

class SiteFilter(django_filters.rest_framework.FilterSet):
    """
    Defining a site filter lets the framework generate query URLs such as
    ?domain=bbc.co.uk.
    """
    # This is nicer than the default, which only lets you input a specific date.
    added_date = django_filters.DateTimeFromToRangeFilter(name='added')
    class Meta:
        model = Site
        fields = ('name', 'domain', 'slug', 'added_date')
