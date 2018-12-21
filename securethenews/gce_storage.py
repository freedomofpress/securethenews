from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage


class StaticStorage(GoogleCloudStorage):
    location = settings.GS_STATIC_PATH


class MediaStorage(GoogleCloudStorage):
    location = settings.GS_MEDIA_PATH
