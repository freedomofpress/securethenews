from wagtail.wagtailcore.signals import page_published, page_unpublished
from wagtail.contrib.wagtailfrontendcache.utils import purge_page_from_cache

from blog.models import BlogPost


def invalidate_frontend_cache_for_blog_index_page(sender, instance, **kwargs):
    """Invalidate the frontend cache for the parent BlogIndexPage of a
    BlogPost."""
    blog_post = instance
    # Recommended way to get parent page from
    # https://github.com/wagtail/wagtail/issues/2779#issuecomment-228472829
    blog_index_page = blog_post.get_parent()
    if blog_index_page:
        purge_page_from_cache(blog_index_page)


page_published.connect(
    invalidate_frontend_cache_for_blog_index_page,
    sender=BlogPost
)
page_unpublished.connect(
    invalidate_frontend_cache_for_blog_index_page,
    sender=BlogPost
)
