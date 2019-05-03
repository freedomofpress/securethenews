from django.db import models
from django.template.defaultfilters import striptags

from wagtail.core import blocks
from wagtail.core.models import Page
from wagtail.core.fields import (StreamField)
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.search import index


class BlogPost(Page):
    date = models.DateField('Publication Date')
    byline = models.CharField(max_length=40)
    body = StreamField([
        ('heading', blocks.CharBlock()),
        ('rich_text', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
    ])

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('byline'),
        StreamFieldPanel('body')
    ]

    parent_page_types = [
        'BlogIndexPage',
    ]

    # It doesn't make sense for BlogPosts to have subpages, and if they did
    # they would not be accessible through any of the navigation anyway.
    subpage_types = []

    @property
    def preview(self):
        """Returns the first sentence of the post, with HTML tags
        stripped, for use as a preview blurb."""
        body_text = striptags(' '.join([
            child.value.source for child in self.body
            if child.block_type == 'rich_text'
        ]))
        sentences = body_text.split('.')
        return '.'.join(sentences[:1]) + '.'


class BlogIndexPage(Page):
    subpage_types = [
        'BlogPost',
    ]

    @property
    def posts(self):
        """Return a list of live blog posts that are children of this
        BlogIndexPage."""
        posts = BlogPost.objects.live().child_of(self)

        # Order by most recent date first
        posts = posts.order_by('-id')

        return posts
