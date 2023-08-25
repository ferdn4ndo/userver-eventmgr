from django.utils.timezone import now

from rest_framework import serializers

from core.models import StorageFileDownload, CustomUser, StorageFile

from core.services.storage.storage_file_service import StorageFileService


class StorageFileDownloadSerializer(serializers.ModelSerializer):
    storage_file = serializers.PrimaryKeyRelatedField(
        queryset=StorageFile.objects.all(),
        write_only=True,
        required=True
    )
    owner = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        write_only=True,
        required=True
    )
    expired = serializers.SerializerMethodField()

    class Meta:
        model = StorageFileDownload
        fields = [
            'id',
            'storage_file',
            'owner',
            'created_at',
            'expires_at',
            'expired',
            'download_url',
            'force_download',
        ]

    def get_expired(self, obj: StorageFileDownload) -> bool:
        return now() > obj.expires_at
