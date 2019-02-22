from __future__ import absolute_import, unicode_literals

import json
import math

from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core import blocks, hooks
from wagtail.core.models import Page
from wagtail.core.fields import (RichTextField,
                                        StreamField)
from wagtail.admin.edit_handlers import (FieldPanel, FieldRowPanel,
                                                MultiFieldPanel, InlinePanel,
                                                PageChooserPanel,
                                                StreamFieldPanel)
from wagtail.contrib.forms.edit_handlers import FormSubmissionsPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.images.blocks import ImageChooserBlock

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
        MultiFieldPanel([FieldPanel('main_title'), FieldPanel('sub_title')],
                        "Main header"),
        MultiFieldPanel([FieldPanel('why_header'), FieldPanel('why_body'),
                         PageChooserPanel('why_learn_more')], "Why section"),
        MultiFieldPanel([FieldPanel('how_header'), FieldPanel('how_body'),
                         PageChooserPanel('how_learn_more')], "How section"),
    ]

    parent_page_types = []

    def get_context(self, request):
        """Special Wagtail method used to add more variables to the
        template context."""
        context = super(HomePage, self).get_context(request)

        # Compute summary statistics
        sites = Site.scanned.all()
        latest_scans = [site.scans.latest() for site in sites]

        sites_offering_https = [scan.site
                                for scan in latest_scans
                                if scan.valid_https
                                and not scan.downgrades_https]

        sites_defaulting_to_https = [scan.site
                                     for scan in latest_scans
                                     if scan.defaults_to_https]

        # Avoid divide by 0 if no Sites have been set up yet
        if sites.count() > 0:
            context['percent_offering_https'] = math.floor(
                len(sites_offering_https) / sites.count() * 100)
            context['percent_defaulting_to_https'] = math.floor(
                len(sites_defaulting_to_https) / sites.count() * 100)
        else:
            context['percent_offering_https'] = 0
            context['percent_defaulting_to_https'] = 0

        context['num_pledged'] = len([site for site in sites if site.pledge])

        # Serialize sites with the results of their latest scans for the teaser
        context['sites_json'] = json.dumps([site.to_dict() for site in sites])

        return context


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
        ('heading', blocks.CharBlock(icon='title')),
        ('rich_text', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('quote', QuoteBlock()),
        ('table', TableBlock()),
    ])

    content_panels = Page.content_panels + [
        FieldPanel('sub_header'),
        StreamFieldPanel('body'),
    ]


@hooks.register('insert_editor_css')
def editor_css():
    # Make 'heading' StreamField blocks look like h2 in RichTextBlocks in the
    # Wagtail Admin.
    return (
        '''
        <style>
            .fieldname-heading input {
                color: #666;
                font-family: Roboto Slab, Georgia, serif;
                font-size: 2.4em;
                font-weight: bold;
            }
        </style>
        '''
    )


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
