from rest_framework import serializers

from api.serializers.generic_audited_model_serializer import GenericAuditedModelSerializer
from core.models import Storage, CustomUser, StorageUser
from core.services.auth.u_server_authentication_service import UServerAuthenticationService


class StorageUserSerializer(GenericAuditedModelSerializer):
    storage = serializers.PrimaryKeyRelatedField(
        queryset=Storage.objects.all(),
        required=True,
        write_only=True
    )
    username = serializers.CharField(
        max_length=255,
        required=True,
        write_only=True,
    )
    system_name = serializers.CharField(
        max_length=255,
        required=True,
        write_only=True,
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        required=False,
    )

    class Meta:
        model = StorageUser
        fields = [
            'id',
            'storage',
            'username',
            'system_name',
            'user',
            'may_write',
            'may_read',
            'created_at',
            'created_by',
            'updated_at',
            'updated_by',
        ]

    def create(self, validated_data):
        service = UServerAuthenticationService()
        user = service.get_user_from_system_name_and_username(
            system_name=validated_data['system_name'],
            username=validated_data['username'],
        )

        validated_data['user'] = user
        del(validated_data['system_name'])
        del(validated_data['username'])

        return super(StorageUserSerializer, self).create(validated_data)
