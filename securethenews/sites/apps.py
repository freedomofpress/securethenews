from django.apps import AppConfig


class SitesConfig(AppConfig):
    name = 'sites'

    def ready(self):
        import sites.signals