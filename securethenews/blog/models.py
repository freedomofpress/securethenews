from django.db import models
from django.template.defaultfilters import striptags, truncatewords

from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import (RichTextField,
                                        StreamField)
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                StreamFieldPanel)
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailsearch import index


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

    @property
    def preview(self):
        """Returns the beginning of the post, truncated, to be used for the post preview on the index page."""
        body_text = ''.join([
            child.value.source for child in self.body
            if child.block_type == 'rich_text'
        ])
        preview_length = 30 # TODO: parameterize in template tag
        return truncatewords(striptags(body_text), preview_length)


class BlogIndexPage(Page):
    subpage_types = [
        'BlogPost',
    ]

    @property
    def posts(self):
        """Return a list of live blog posts that are descendants of this page."""
        posts = BlogPost.objects.live().descendant_of(self)

        # Order by most recent date first
        posts = posts.order_by('-date')

        return posts
