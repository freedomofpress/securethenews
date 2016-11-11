from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from .models import Pledge


class PledgeAdmin(ModelAdmin):
    model = Pledge
    menu_label = 'Pledges'
    menu_icon = 'form'
    add_to_settings_menu = False

    list_display = ('site', 'timestamp', 'review_status')
    list_filter = ('review_status',)

    search_fields = ('url', 'contact_email')

    def get_queryset(self, request):
        """Only display confirmed pledges."""
        qs = super(PledgeAdmin, self).get_queryset(request)
        return qs.filter(confirmed=True)


modeladmin_register(PledgeAdmin)
