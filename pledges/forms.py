import re
from urllib.parse import urlparse
from urllib.request import urlopen, HTTPError

from django.forms import ModelForm, ValidationError

from .models import Pledge


class PledgeForm(ModelForm):
    class Meta:
        model = Pledge
        fields = ['site', 'url', 'contact_email']

    def clean(self):
        # To discourage spam and make moderation easier, we require:

        # 1. The URL should match the domain of the site
        site = self.cleaned_data['site']
        domain_re = r'([\w\.]+\.)?{}'.format(site.domain.replace('.', r'\.'))
        parsed_url = urlparse(self.cleaned_data['url'])
        if not re.match(domain_re, parsed_url.netloc):
            raise ValidationError(
                'URL domain must match or be a subdomain of the site domain.'
            )

        # 2. The contact email address should match the domain of the site
        email_re = '.+@{}'.format(site.domain.replace('.', r'\.'))
        if not re.match(email_re, self.cleaned_data['contact_email']):
            raise ValidationError(
                'Contact email address must match the site domain.'
            )

        # 3. The URL of the statement of intent should point to a live page
        try:
            urlopen(self.cleaned_data['url'])
        except HTTPError:
            raise ValidationError(
                'URL must be accessible.'
            )
