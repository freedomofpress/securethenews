from whitenoise.storage import CompressedManifestStaticFilesStorage


class FilesStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False
