from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Site

class SiteAdmin(ModelAdmin):
    model = Site
    menu_label = 'News Sites'
    menu_icon = 'date'
    add_to_settings_menu = False
    search_fields = ('name', 'domain')

modeladmin_register(SiteAdmin)
