"""
Serializers are used by the REST framework to generate the API output
(and potentially to deserialize input, if we want to make the API writable
in future).
"""
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from sites.models import Site, Scan, Region
from urllib.parse import urljoin
from django.urls import reverse


class ScanSerializer(serializers.ModelSerializer):
    """
    Used for the latest_scan representation in a site view, as well as for
    the /sites/<domain>/scans list of all scans for a given domain.
    """
    grade = serializers.SerializerMethodField()

    class Meta:
        model = Scan
        # We don't need to expose the detailed program output, or the internal
        # IDs
        exclude = ('pshtt_stdout', 'pshtt_stderr', 'site', 'id')

    def get_grade(self, data):
        return data.grade['grade']


class RegionSerializer(serializers.ModelSerializer):
    """
    Used for the region representation in a site view
    """

    class Meta:
        model = Region
        fields = ('name', 'icon', 'slug')


class SiteSerializer(serializers.ModelSerializer):

    # In production, a site can have a lot of scans, so we don't want to expose
    # all of them in most cases. SerializerMethodField lets us add a filtered
    # query set to the output.
    latest_scan = serializers.SerializerMethodField()
    all_scans = serializers.SerializerMethodField()
    regions = serializers.SerializerMethodField()

    class Meta:
        model = Site
        fields = ('name', 'slug', 'domain', 'added', 'regions',
                  'latest_scan', 'all_scans')

    def get_latest_scan(self, data):
        try:
            latest = data.scans.latest()
        except ObjectDoesNotExist:
            return None

        # Run the data through the standard serializer above
        serializer_latest = ScanSerializer(instance=latest)
        return serializer_latest.data

    def get_all_scans(self, data):
        urlroot = reverse('api-root-v1')
        relative_url = urljoin(urlroot, 'sites/' + data.domain + '/scans/')
        return self.context['request'].build_absolute_uri(relative_url)

    def get_regions(self, data):
        regions = []
        for region in data.regions.all():
            serializer_region = RegionSerializer(instance=region)
            regions.append(serializer_region.data)
        return regions
