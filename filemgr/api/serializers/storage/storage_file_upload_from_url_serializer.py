from rest_framework import serializers

from api.serializers.storage.storage_file_upload_from_file_serializer import StorageFileUploadFromFileSerializer


class StorageFileUploadFromUrlSerializer(StorageFileUploadFromFileSerializer):
    url = serializers.URLField()
