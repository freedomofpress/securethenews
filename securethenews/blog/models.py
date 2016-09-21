from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailsearch import index


class BlogPost(Page):
    date = models.DateField('Publication Date')
    byline = models.CharField(max_length=40)
    body = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('byline'),
        FieldPanel('body', classname='full')
    ]

    parent_page_types = [
        'BlogIndexPage',
    ]


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
