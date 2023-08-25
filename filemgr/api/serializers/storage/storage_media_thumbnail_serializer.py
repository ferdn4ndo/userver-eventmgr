from rest_framework import serializers

from api.serializers.generic_audited_model_serializer import GenericAuditedModelSerializer
from core.models.storage.storage_media_thumbnail_model import StorageMediaThumbnail
from core.services.storage.storage_file_service import StorageFileService


class StorageMediaThumbnailSerializer(GenericAuditedModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = StorageMediaThumbnail
        fields = [
            'id',
            'media',
            'size_tag',
            'storage_file',
            'height',
            'width',
            'megapixels',
            'image_url',
            'created_at',
            'updated_at',
        ]

    def get_image_url(self, obj):
        """
        Retrieves the signed URL to view the thumbnail
        """
        driver = StorageFileService(storage_file=obj.storage_file).load_driver()

        return driver.get_download_url(file=obj.storage_file)
