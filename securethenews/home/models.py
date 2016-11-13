from __future__ import absolute_import, unicode_literals

import json
import math

from django.db import models

from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import (RichTextField,
                                        StreamField)
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                MultiFieldPanel,
                                                InlinePanel,
                                                PageChooserPanel,
                                                StreamFieldPanel)
from wagtail.wagtailimages.blocks import ImageChooserBlock

from sites.models import Site


class HomePage(Page):
    main_title = models.CharField(max_length=50, default="Every news site should be secure.")
    sub_title = models.CharField(max_length=50, default="It's critical for both journalists and readers.")
    how_header = models.CharField(max_length=50, default="Switching to HTTPS is easier than ever")
    why_header = models.CharField(max_length=50, default="Encryption protects your readers")
    how_body = RichTextField(default="Blah blah")
    why_body = RichTextField(default="Blah blah")

    content_panels = Page.content_panels + [
        MultiFieldPanel([ FieldPanel('main_title'), FieldPanel('sub_title') ], "Main header"),
        MultiFieldPanel([ FieldPanel('how_header'), FieldPanel('how_body') ], "How section"),
        MultiFieldPanel([ FieldPanel('why_header'), FieldPanel('why_body') ], "Why section"),
    ]

    parent_page_types = []

    def get_context(self, request):
        """Special Wagtail method used to add more variables to the template context."""
        context = super(HomePage, self).get_context(request)

        # Compute summary statistics
        sites = Site.objects.all()
        latest_scans = [ site.scans.latest() for site in sites ]

        sites_offering_https = [ scan.site
                                 for scan in latest_scans
                                 if scan.valid_https
                                 and not scan.downgrades_https ]

        sites_defaulting_to_https = [ scan.site
                                      for scan in latest_scans
                                      if scan.defaults_to_https ]

        total_sites = Site.objects.count()

        context['percent_offering_https'] = math.floor(
            len(sites_offering_https) / total_sites * 100)
        context['percent_defaulting_to_https'] = math.floor(
            len(sites_defaulting_to_https) / total_sites * 100)

        context['num_pledged'] = len([ site for site in sites if site.pledge ])

        # Serialize sites with the results of their latest scans for the teaser
        context['sites_json'] = json.dumps([site.to_dict() for site in sites])

        return context

class ContentPage(Page):
    sub_header = models.CharField(max_length=50, default="")
    body = StreamField([
        ('heading', blocks.CharBlock()),
        ('rich_text', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ])
    button_text = models.CharField(max_length=50, null=True, blank=True)
    button_target = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL)

    content_panels = Page.content_panels + [
        FieldPanel('sub_header'),
        StreamFieldPanel('body'),
        MultiFieldPanel([ FieldPanel('button_text'), PageChooserPanel('button_target') ], "Call to action"),
    ]
