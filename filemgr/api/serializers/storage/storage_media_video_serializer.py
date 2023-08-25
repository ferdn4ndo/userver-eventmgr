from core.models.storage.storage_media_video_model import StorageMediaVideo

from api.serializers.generic_audited_model_serializer import GenericAuditedModelSerializer


class StorageMediaVideoSerializer(GenericAuditedModelSerializer):

    class Meta:
        model = StorageMediaVideo
        fields = [
            'id',
            'fps',
            'duration',
            'size_tag',
            'height',
            'width',
            'created_at',
            'updated_at',
        ]
