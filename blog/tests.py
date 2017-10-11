import datetime
from unittest import mock

from django.test import TestCase

from wagtail.wagtailcore.models import Page

from .models import BlogIndexPage, BlogPost


class TestBlogIndexPage(TestCase):

    def setUp(self):
        home_page = Page.objects.get(slug='home')

        blog_index_page = BlogIndexPage(
            title='Blog',
            slug='blog',
            show_in_menus=True
        )
        home_page.add_child(instance=blog_index_page)

        blog_posts = [
            BlogPost(title='First Blog Post',
                     slug='first-blog-post',
                     date=datetime.date.today(),
                     byline='Author'),
            BlogPost(title='Second Blog Post',
                     slug='second-blog-post',
                     date=datetime.date.today(),
                     byline='Author')
        ]

        for blog_post in blog_posts:
            blog_index_page.add_child(instance=blog_post)

    def test_ordering_of_same_day_blogs_on_index(self):
        """Verify that blog posts posted on the same day are ordered with
        the most recent at the top of the page."""

        blog_index = BlogIndexPage.objects.first()

        self.assertEqual(blog_index.posts[0].title, 'Second Blog Post')
        self.assertEqual(blog_index.posts[1].title, 'First Blog Post')

    @mock.patch('blog.signals.purge_page_from_cache')
    def test_frontend_cache_invalidation(self, mock_purge_page_from_cache):
        """When a BlogPost is published or unpublished, we should invalidate
        the frontend cache for the corresponding BlogIndexPage."""
        blog_index_page = BlogIndexPage.objects.first()
        new_blog_post = BlogPost(
            title='New Blog Post',
            slug='new-blog-post',
            date=datetime.date.today(),
            byline='Author'
        )
        blog_index_page.add_child(instance=new_blog_post)

        # Publishing a BlogPost should trigger frontend cache invalidation for
        # the corresponding BlogIndexPage.
        #
        # XXX: For some reason, Wagtail uses the generic Page object as the
        # instance for the page_published signal, but uses the specific object
        # (e.g. BlogIndexPage) as the instance for the page_unpublished signal.
        # You can get the generic Page object from a specific object with
        # .page_ptr, or go the other way with .specific. For more, see:
        # http://docs.wagtail.io/en/v1.8/topics/pages.html#working-with-pages
        new_blog_post.save_revision().publish()
        mock_purge_page_from_cache.assert_called_once_with(
                                            blog_index_page.page_ptr)

        # Unpublishing the BlogPost should also trigger frontend cache
        # invalidation for the corresponding BlogIndexPage.
        mock_purge_page_from_cache.reset_mock()
        new_blog_post.unpublish()
        mock_purge_page_from_cache.assert_called_once_with(blog_index_page)
