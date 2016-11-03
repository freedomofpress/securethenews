from django.forms import ModelForm

from .models import Pledge

class PledgeForm(ModelForm):
    class Meta:
        model = Pledge
        fields = ['site', 'url', 'contact_email']
