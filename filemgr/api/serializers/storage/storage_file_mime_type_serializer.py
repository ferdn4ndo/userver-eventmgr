from rest_framework import serializers

from core.models.storage.storage_file_mime_type_model import StorageFileMimeType


class StorageFileMimeTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = StorageFileMimeType
        fields = [
            'mime_type',
            'generic_type',
            'description',
            'extensions',
        ]
