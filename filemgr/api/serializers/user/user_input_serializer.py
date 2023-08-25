from rest_framework import serializers


class UserInputSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True)
