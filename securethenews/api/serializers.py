from rest_framework import serializers
from sites.models import Site, Scan

"""
Serializers are used by the REST framework to generate the API output
(and potentially to deserialize input, if we want to make the API writable
in future).
"""

class ScanSerializer(serializers.ModelSerializer):
    """
    We don't allow direct API access to scans; this serializer is only used
    to generate the nested representation within a site object.
    """
    class Meta:
        model = Scan
        # We don't need to expose the detailed program output, or the internal
        # IDs
        exclude = ('pshtt_stdout', 'pshtt_stderr', 'site', 'id')

class SiteSerializer(serializers.ModelSerializer):
    scans = ScanSerializer(many=True)
    class Meta:
        model = Site
        fields = ('name', 'slug', 'domain', 'added', 'scans')
