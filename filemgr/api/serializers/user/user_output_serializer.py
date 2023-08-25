from rest_framework import serializers

from core.models.user.user_model import CustomUser


class UserOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'uuid',
            'username',
            'registered_at',
            'last_activity_at',
        ]
