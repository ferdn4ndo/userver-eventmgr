from rest_framework import serializers

from api.serializers.storage.storage_file_mime_type_serializer import StorageFileMimeTypeSerializer
from core.models.storage.storage_model import Storage
from core.models.storage.storage_file_model import StorageFile
from api.serializers.user.user_serializer import UserSerializer


class StorageFileSerializer(serializers.ModelSerializer):
    signature_key = serializers.ReadOnlyField()
    storage = serializers.PrimaryKeyRelatedField(
        write_only=True,
        required=True,
        queryset=Storage.objects.all
    )
    owner = UserSerializer(read_only=True)
    status = serializers.ReadOnlyField()
    size = serializers.ReadOnlyField()
    hash = serializers.ReadOnlyField()
    type = StorageFileMimeTypeSerializer(read_only=True)
    origin = serializers.ReadOnlyField()
    original_path = serializers.ReadOnlyField()
    real_path = serializers.ReadOnlyField()
    available = serializers.ReadOnlyField()
    excluded = serializers.ReadOnlyField()

    class Meta:
        model = StorageFile
        fields = [
            'id',
            'signature_key',
            'storage',
            'owner',
            'name',
            'status',
            'visibility',
            'size',
            'hash',
            'type',
            'exif_metadata',
            'custom_metadata',
            'origin',
            'original_path',
            'real_path',
            'virtual_path',
            'available',
            'excluded',
            'created_by',
            'created_at',
            'updated_by',
            'updated_at',
        ]
