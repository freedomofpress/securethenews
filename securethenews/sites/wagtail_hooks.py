from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Site, Pledge

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

class PledgeAdmin(ModelAdmin):
    model = Pledge
    menu_label = 'Pledges'
    menu_icon = 'form'
    add_to_settings_menu = False

    list_display = ('site', 'timestamp', 'approved')
    list_filter = ('approved',)
    ordering = ('approved',)

    search_fields = ('url', 'contact_email')

modeladmin_register(SiteAdmin)
modeladmin_register(PledgeAdmin)
