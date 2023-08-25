from api.exceptions.internal_server_exception import InternalServerException
from api.serializers.generic_audited_model_serializer import GenericAuditedModelSerializer
from api.serializers.storage.storage_media_document_serializer import StorageMediaDocumentSerializer
from api.serializers.storage.storage_media_image_serializer import StorageMediaImageSerializer
from api.serializers.storage.storage_media_thumbnail_serializer import StorageMediaThumbnailSerializer
from api.serializers.storage.storage_media_video_serializer import StorageMediaVideoSerializer

from core.models.storage.storage_media_document_model import StorageMediaDocument
from core.models.storage.storage_media_image_model import StorageMediaImage
from core.models.storage.storage_media_model import StorageMedia
from core.models.storage.storage_media_video_model import StorageMediaVideo


class StorageMediaSerializer(GenericAuditedModelSerializer):
    thumbnails = StorageMediaThumbnailSerializer(many=True, read_only=True)

    class Meta:
        model = StorageMedia
        fields = [
            'id',
            'title',
            'type',
            'description',
            'storage_file',
            'thumbnails',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
        ]

    def to_representation(self, instance: StorageMedia):
        instance_dict = super(StorageMediaSerializer, self).to_representation(instance)
        instance_dict['metadata'] = {}

        if instance.type == StorageMedia.MediaType.IMAGE:
            model = StorageMediaImage
            serializer = StorageMediaImageSerializer
        elif instance.type == StorageMedia.MediaType.VIDEO:
            model = StorageMediaVideo
            serializer = StorageMediaVideoSerializer
        elif instance.type == StorageMedia.MediaType.DOCUMENT:
            model = StorageMediaDocument
            serializer = StorageMediaDocumentSerializer
        else:
            return instance_dict

        item_queryset = model.objects.filter(media=instance)
        if item_queryset.count() == 1:
            instance_dict['metadata'] = serializer(item_queryset[0]).data
        else:
            raise InternalServerException(
                "Database inconsistency: found {} {} objects for StorageMedia ID {} (must have exactly one)".format(
                    item_queryset.count(), model.__class__, instance.id,
                )
            )

        return instance_dict
