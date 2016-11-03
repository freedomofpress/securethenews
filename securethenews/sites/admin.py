from django.contrib import admin

from .models import Site, Scan, Pledge

admin.site.register(Site)
admin.site.register(Scan)
admin.site.register(Pledge)
