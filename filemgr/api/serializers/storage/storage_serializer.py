from json import JSONEncoder

from django.db.models import Sum
from rest_framework import serializers

from core.models import Storage, StorageFile


class StorageSerializer(serializers.ModelSerializer):
    credentials = serializers.JSONField(required=True, write_only=True, encoder=JSONEncoder)
    total_size = serializers.SerializerMethodField()

    class Meta:
        model = Storage
        fields = [
            'id',
            'type',
            'credentials',
            'media_convert_configuration',
            'total_size',
        ]

    def get_total_size(self, obj: Storage) -> int:
        total_size_selector = StorageFile.objects.filter(storage=obj, excluded=False).aggregate(Sum('size'))
        if total_size_selector['size__sum'] is None:
            return 0
        return int(total_size_selector['size__sum'])
