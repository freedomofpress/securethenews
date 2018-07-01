from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = settings.AWS_S3_STATIC_PATH
    access_key = False
    secret_key = False


class MediaStorage(S3Boto3Storage):
    location = settings.AWS_S3_MEDIA_PATH
    access_key = False
    secret_key = False
