import os

from django.contrib.auth.models import User
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from core.models import StorageFile
from api.serializers.user.user_serializer import UserSerializer
from api.services.policy import IsLoggedIn, IsAdminOrDeny


class UsersAdminViewSet(viewsets.ViewSet):
    permission_classes = [IsLoggedIn, IsAdminOrDeny]

    def list(self, request: Request) -> Response:
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def create(self, request: Request) -> Response:
        data = request.data
        data['system_name'] = os.environ['USERVER_AUTH_SYSTEM_NAME']
        data['is_admin'] = False
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)

    def retrieve(self, request: Request, pk: str) -> Response:
        queryset = User.objects.all()
        storage = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(storage)
        info_dict = serializer.data
        total_size_selector = StorageFile.objects.filter(
            storage=storage, excluded=False, owner=request.user
        ).aggregate(Sum('size'))
        info_dict['total_size'] = total_size_selector['size__sum']
        return Response(info_dict, status.HTTP_200_OK)

    def partial_update(self, request: Request, pk: str) -> Response:
        queryset = User.objects.all()
        storage = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(storage, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    def destroy(self, request: Request, pk: str) -> Response:
        queryset = User.objects.all()
        storage = get_object_or_404(queryset, pk=pk)
        storage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
