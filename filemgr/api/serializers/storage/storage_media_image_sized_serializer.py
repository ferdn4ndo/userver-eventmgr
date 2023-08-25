from rest_framework import serializers

from core.models.storage.storage_file_model import StorageFile
from core.models.storage.storage_media_image_sized_model import StorageMediaImageSized

from api.serializers.generic_audited_model_serializer import GenericAuditedModelSerializer


class StorageMediaImageSizedSerializer(GenericAuditedModelSerializer):
    storage_file = serializers.PrimaryKeyRelatedField(queryset=StorageFile.objects.all())

    class Meta:
        model = StorageMediaImageSized
        fields = [
            'id',
            'storage_file',
            'size_tag',
            'height',
            'width',
            'megapixels',
            'created_at',
            'updated_at',
        ]
