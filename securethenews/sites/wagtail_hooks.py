from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Site

class SiteAdmin(ModelAdmin):
    model = Site
    menu_label = 'News Sites'
    menu_icon = 'site'
    add_to_settings_menu = False

    list_display = ('name', 'domain', 'score')

    def score(self, obj):
        return '{} / 100'.format(obj.scans.latest().score)
    score.short_description = 'Score'

    search_fields = ('name', 'domain')

modeladmin_register(SiteAdmin)
