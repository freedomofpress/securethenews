import datetime

from django.test import TestCase

from wagtail.wagtailcore.models import Page

from .models import BlogIndexPage, BlogPost


class BlogTest(TestCase):
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
        """Verify that blog posts posted on the same day are ordered with the most recent at the top of the page."""

        blog_index = BlogIndexPage.objects.first()

        self.assertEqual(blog_index.posts[0].title, 'Second Blog Post')
        self.assertEqual(blog_index.posts[1].title, 'First Blog Post')
