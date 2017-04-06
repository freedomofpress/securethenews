"""
Django REST Framework views for the API
"""
from . import serializers, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import routers, viewsets, generics, filters as rest_framework_filters
from sites.models import Site
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

# NOTE: Method docstrings in this file are used by the framework to generate
# page subtitles


@api_view(['GET'])
def api_root(request, format=None):
    """
    Index of available API calls
    """

    return Response({
        'sites': reverse('site-list', request=request, format=format),
    })


class SiteList(generics.ListAPIView):
    """
    List of all SecureTheNews sites and the latest scan results for them
    """
    queryset = Site.objects.all()
    serializer_class = serializers.SiteSerializer
    filter_class = filters.SiteFilter

    # Declaring the ordering filter lets users define ascending/descending
    # order on selected fields, using the ?ordering= parameter
    # Note that the two filters reside in different modules.
    filter_backends = (rest_framework_filters.OrderingFilter,
                       DjangoFilterBackend,)
    ordering_fields = ('added', 'name', 'domain')


class SiteDetail(generics.RetrieveAPIView):
    """
    Individual SecureTheNews site and its latest scan results
    """
    serializer_class = serializers.SiteSerializer

    # By default only /site/<primary key> would work, but we want domain names
    # to be used instead.
    lookup_field = 'domain'

    def get_queryset(self):
        # Passed in via URL regexp in urls.py
        domain = self.kwargs['domain']
        return Site.objects.filter(domain=domain)
