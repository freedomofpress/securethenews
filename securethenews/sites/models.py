from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel

from scans.models import Site

class SitePage(Page):
    site_url = models.CharField(
        'URL',
        max_length=255,
        unique=True,
        null=True,
        help_text='Specify the domain name without the scheme, e.g. "example.com" instead of "https://example.com"')
    added = models.DateTimeField(auto_now_add=True, null=True)

    site = models.OneToOneField(
        Site,
        on_delete=models.PROTECT,
        related_name='page')

    content_panels = Page.content_panels + [
        FieldPanel('site_url')
    ]

    def save(self, *args, **kwargs):
        self.sync_site()
        return super().save(*args, **kwargs)

    def sync_site(self):
        if not hasattr(self, 'site'):
            site = Site(name=self.title, url=self.site_url)
            site.save()
            self.site = site
        else:
            self.site.name = self.title
            self.site.url = self.site_url
            self.site.save()


