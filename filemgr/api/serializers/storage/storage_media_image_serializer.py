from api.serializers.generic_audited_model_serializer import GenericAuditedModelSerializer
from api.serializers.storage.storage_media_image_sized_serializer import StorageMediaImageSizedSerializer

from core.models.storage.storage_media_image_model import StorageMediaImage


class StorageMediaImageSerializer(GenericAuditedModelSerializer):
    sized_images = StorageMediaImageSizedSerializer(many=True, read_only=True)

    class Meta:
        model = StorageMediaImage
        fields = [
            'id',
            'focal_length',
            'aperture',
            'flash_fired',
            'iso',
            'orientation_angle',
            'is_flipped',
            'exposition',
            'datetime_taken',
            'camera_manufacturer',
            'camera_model',
            'exif_image_height',
            'exif_image_width',
            'size_tag',
            'height',
            'width',
            'megapixels',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
            'sized_images',
        ]
