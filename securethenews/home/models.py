from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                MultiFieldPanel,
                                                InlinePanel,
                                                PageChooserPanel)

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


class ContentPage(Page):
    sub_header = models.CharField(max_length=50, default="")
    body = RichTextField(default="")
    button_text = models.CharField(max_length=50, null=True, blank=True)
    button_target = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL)

    content_panels = Page.content_panels + [
        FieldPanel('sub_header'),
        FieldPanel('body'),
        MultiFieldPanel([ FieldPanel('button_text'), PageChooserPanel('button_target') ], "Call to action"),
    ]
