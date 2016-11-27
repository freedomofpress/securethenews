from __future__ import absolute_import, unicode_literals

import json
import math

from django.db import models
from django.utils.html import format_html

from modelcluster.fields import ParentalKey
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.wagtailcore import blocks, hooks
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import (RichTextField,
                                        StreamField)
from wagtail.wagtailadmin.edit_handlers import (FieldPanel, FieldRowPanel,
    MultiFieldPanel, InlinePanel, PageChooserPanel, StreamFieldPanel)
from wagtail.wagtailforms.edit_handlers import FormSubmissionsPanel
from wagtail.wagtailforms.models import AbstractEmailForm, AbstractFormField
from wagtail.wagtailimages.blocks import ImageChooserBlock

from sites.models import Site


class HomePage(Page):
    main_title = models.TextField(default="")
    sub_title = models.TextField(default="")

    why_header = models.TextField(default="")
    why_body = models.TextField(default="")
    why_learn_more = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    how_header = models.TextField(default="")
    how_body = models.TextField(default="")
    how_learn_more = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([ FieldPanel('main_title'), FieldPanel('sub_title') ], "Main header"),
        MultiFieldPanel([ FieldPanel('why_header'), FieldPanel('why_body'), PageChooserPanel('why_learn_more') ], "Why section"),
        MultiFieldPanel([ FieldPanel('how_header'), FieldPanel('how_body'), PageChooserPanel('how_learn_more') ], "How section"),
    ]

    parent_page_types = []

    def get_context(self, request):
        """Special Wagtail method used to add more variables to the template context."""
        context = super(HomePage, self).get_context(request)

        # Compute summary statistics
        sites = Site.scanned.all()
        latest_scans = [ site.scans.latest() for site in sites ]

        sites_offering_https = [ scan.site
                                 for scan in latest_scans
                                 if scan.valid_https
                                 and not scan.downgrades_https ]

        sites_defaulting_to_https = [ scan.site
                                      for scan in latest_scans
                                      if scan.defaults_to_https ]

        # Avoid divide by 0 if no Sites have been set up yet
        if sites.count() > 0:
            context['percent_offering_https'] = math.floor(
                len(sites_offering_https) / sites.count() * 100)
            context['percent_defaulting_to_https'] = math.floor(
                len(sites_defaulting_to_https) / sites.count() * 100)
        else:
            context['percent_offering_https'] = 0
            context['percent_defaulting_to_https'] = 0

        context['num_pledged'] = len([ site for site in sites if site.pledge ])

        # Serialize sites with the results of their latest scans for the teaser
        context['sites_json'] = json.dumps([site.to_dict() for site in sites])

        return context


class HeadingLevelChoiceBlock(blocks.ChoiceBlock):
    choices = (
        ('h1', 'H1'),
        ('h2', 'H2'),
        ('h3', 'H3'),
        ('h4', 'H4'),
        ('h5', 'H5'),
        ('h6', 'H6'),
    )


class HeadingBlock(blocks.StructBlock):
    heading = blocks.CharBlock(classname='title')
    level = HeadingLevelChoiceBlock(default='h1')

    class Meta:
        icon = 'title'


class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock()
    source = blocks.CharBlock()
    link = blocks.URLBlock(required=False)

    class Meta:
        icon = 'openquote'
        template = 'home/blocks/quote.html'


class ContentPage(Page):
    sub_header = models.CharField(max_length=50, default="")
    body = StreamField([
        ('heading', HeadingBlock()),
        ('rich_text', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', QuoteBlock()),
        ('table', TableBlock()),
    ])

    content_panels = Page.content_panels + [
        FieldPanel('sub_header'),
        StreamFieldPanel('body'),
    ]


class FormField(AbstractFormField):
    page = ParentalKey('FormPage', related_name='form_fields')


class FormPage(AbstractEmailForm):
    sub_header = models.TextField(default="")
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel('sub_header'),
        FieldPanel('intro', classname='full'),
        InlinePanel('form_fields', label='Form fields'),
        FieldPanel('thank_you_text', classname='full'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname='col6'),
                FieldPanel('to_address', classname='col6'),
            ]),
            FieldPanel('subject')
        ], 'Email'),
    ]
