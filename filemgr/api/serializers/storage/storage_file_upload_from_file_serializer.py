from rest_framework import serializers

from core.models.storage.storage_file_model import StorageFile


class StorageFileUploadFromFileSerializer(serializers.Serializer):
    virtual_path = serializers.CharField(max_length=1024, default="")
    name = serializers.CharField(max_length=1024, default="")
    overwrite = serializers.BooleanField(default=False)
    visibility = serializers.ChoiceField(
        choices=StorageFile.FileVisibility.choices,
        default=StorageFile.FileVisibility.USER
    )

    def update(self, instance, validated_data):
        """
        Overriding the default ORM update behavior as this serializer won't handle database objects
        """
        pass

    def create(self, validated_data):
        """
        Overriding the default ORM create behavior as this serializer won't handle database objects
        """
        pass
