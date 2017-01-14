import datetime
from os.path import abspath, join, dirname

from django.contrib.auth.models import User
from django.core import management
from django.core.management.base import BaseCommand
from django.db import transaction

from wagtail.wagtailcore.models import Page, Site

from wagtailmenus.models import MainMenu, MainMenuItem

from home.models import HomePage, ContentPage
from blog.models import BlogIndexPage, BlogPost


class Command(BaseCommand):
    help = 'Populates the database with data for development'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Creating development data... ', '')
        self.stdout.flush()

        # Delete the default home page
        Page.objects.get(slug='home').delete()

        # Basic setup
        root_page = Page.objects.get(title='Root')

        home_page = HomePage(
            title='Home',
            slug='home',
            main_title='Every news site should be secure.',
            sub_title='HTTPS encryption enables security, privacy, and prevents censorship. '
                      'We’re tracking its adoption.',
            why_header='HTTPS protects your privacy and security',
            why_body="With HTTPS enabled by default you can protect reader privacy, improve your website's security, "
                     "better protect your sources, prevent censorship, improve your search rankings, provide a better "
                     "user experience, see your website loading speeds potentially increase, and avoid Google shaming.",
            how_header='Resources for switching your news site over to HTTPS',
            how_body="Switching your news site over to HTTPS is not as simple as flicking a switch. But a handful of "
                     "news organizations have already pioneered the effort and have shared their tips and tricks for "
                     "making it as smooth as possible. We've documented them here."
        )
        root_page.add_child(instance=home_page)

        site = Site.objects.create(
            site_name='Freedom of the Press (Dev)',
            hostname='localhost',
            port='8000',
            root_page=home_page,
            is_default_site=True
        )

        # Add "Why?" and "How" pages, since they're so prominently featured on the home page.
        why_page = ContentPage(
            title='Why?',
            slug='why',
            sub_header='10 good reasons to switch your site to HTTPS',
            show_in_menus=True
        )
        home_page.add_child(instance=why_page)

        how_page = ContentPage(
            title='How',
            slug='how',
            sub_header='Resources and tips for deploying HTTPS by default',
            show_in_menus=True
        )
        home_page.add_child(instance=how_page)

        # Add a BlogIndexPage and an example BlogPost
        blog_index_page = BlogIndexPage(
            title='Blog',
            slug='blog',
            show_in_menus=True
        )
        home_page.add_child(instance=blog_index_page)

        blog_post = BlogPost(
            title='Test Blog Post',
            slug='test-blog-post',
            date=datetime.date.today(),
            byline='Dog with a Blog'
        )
        blog_index_page.add_child(instance=blog_post)

        # Main menu via wagtailmenus
        # Remember: Pages must have `show_in_menus=True` *and* a corresponding MainMenuItem to show up
        main_menu = MainMenu.objects.create(site=site)

        why_menu_item = MainMenuItem.objects.create(
            menu=main_menu,
            link_text='Why?',
            link_page=why_page
        )
        how_menu_item = MainMenuItem.objects.create(
            menu=main_menu,
            link_text='How',
            link_page=how_page
        )
        blog_index_menu_item = MainMenuItem.objects.create(
            menu=main_menu,
            link_text='Blog',
            link_page=blog_index_page
        )

        # Load sites from CSV file stored in Git repo
        self.stdout.write('Loading sites from news_sites.csv... ', '')
        news_sites_csv = abspath(join(dirname(__file__), '../../../../news_sites.csv'))
        management.call_command('loadsites', news_sites_csv)

        # TODO There are several limitations with this approach:
        # 1. `manage.py createdevdata` now requires internet access, in order to run the scan command.
        # 2. Scanning all of the sites in news_sites.csv takes several minutes. Ideally, createdevdata would be as fast
        #    as possible to facilitate rapid development and testing.
        # 3. This only creates one set of scans in the database. For some functionality, it is or will be useful to
        #    have multiple sets of scans set up initially.
        self.stdout.write('Scanning sites from news_sites.csv (this may take a while)...')
        management.call_command('scan')

        # Create superuser
        User.objects.create_superuser(
            'test',
            'test@freedom.press',
            'test',
        )
