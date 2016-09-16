from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailsearch import index

class BlogPost(Page):
    date = models.DateField('Publication Date')
    intro = models.CharField(max_length=255)
    byline = models.CharField(max_length=40)
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('byline'),
        FieldPanel('intro'),
        FieldPanel('body', classname='full')
    ]
