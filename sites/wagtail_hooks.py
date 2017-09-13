from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Site


class SiteAdmin(ModelAdmin):
    model = Site
    menu_label = 'News Sites'
    menu_icon = 'site'
    add_to_settings_menu = False

    list_display = ('name', 'domain', 'score', 'grade')

    def score(self, obj):
        return '{} / 100'.format(obj.scans.latest().score)
    score.short_description = 'Score'

    def grade(self, obj):
        return obj.scans.latest().grade['grade']
    grade.short_description = 'Grade'

    search_fields = ('name', 'domain')


modeladmin_register(SiteAdmin)
