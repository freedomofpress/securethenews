from django.apps import AppConfig


class PledgesConfig(AppConfig):
    name = 'pledges'

    def ready(self):
        from . import signals
