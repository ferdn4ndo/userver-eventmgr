from django.db.models import Q
from rest_framework import serializers
from rest_framework.request import Request

from app.models.storage.storage_file_image_model import StorageFileImage, StorageFileImageDimensions
from app.models.storage.storage_file_model import StorageFile
from app.models.storage.storage_model import Storage
from app.serializers.storage_file_serializer import StorageFileSerializer


class StorageFileImageDimensionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = StorageFileImageDimensions
        fields = [
            'tag',
            'name',
            'description',
            'height',
            'width',
            'megapixels',
        ]


class StorageFileImageSerializer(serializers.ModelSerializer):
    storage_file = StorageFileSerializer()
    dimensions = StorageFileImageDimensionsSerializer()

    class Meta:
        model = StorageFileImage
        fields = [
            'id',
            'storage_file',
            'height',
            'width',
            'dimensions',
        ]

    @staticmethod
    def get_filtered_queryset(request: Request, storage: Storage):
        return StorageFileImage.objects.filter(storage_file__storage=storage).filter(
            Q(storage_file__visibility=StorageFile.FileVisibility.PUBLIC) |
            (
                Q(storage_file__visibility=StorageFile.FileVisibility.SYSTEM) &
                Q(storage_file__owner__system_name=request.user.system_name)
            ) |
            (
                Q(storage_file__visibility=StorageFile.FileVisibility.USER) &
                Q(storage_file__owner=request.user)
            )
        )
