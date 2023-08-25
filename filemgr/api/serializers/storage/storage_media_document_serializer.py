from api.serializers.generic_audited_model_serializer import GenericAuditedModelSerializer
from core.models.storage.storage_media_document_model import StorageMediaDocument


class StorageMediaDocumentSerializer(GenericAuditedModelSerializer):

    class Meta:
        model = StorageMediaDocument
        fields = [
            'id',
            'pages',
            'black_and_white',
            'created_at',
            'updated_at',
        ]
