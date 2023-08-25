from rest_framework import serializers

from api.serializers.generic_model_serializer import GenericModelSerializer
from core.models.user.user_model import CustomUser


class GenericAuditedModelSerializer(GenericModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        required=False,
        allow_null=True,
    )
    created_at = serializers.DateTimeField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        required=False,
        allow_null=True,
    )
    updated_at = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )
