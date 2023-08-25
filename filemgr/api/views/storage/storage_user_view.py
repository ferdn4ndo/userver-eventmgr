from django.db.models import QuerySet
from rest_framework.request import Request
from rest_framework.response import Response

from api.models import get_object_or_404
from api.policies.is_admin_or_deny_policy import IsAdminOrDenyPolicy
from api.serializers.storage.storage_user_serializer import StorageUserSerializer
from api.views.generic_create_read_destroy_model_view import GenericCreateReadDestroyModelViewSet
from core.models import StorageUser, Storage


class StorageUserViewSet(GenericCreateReadDestroyModelViewSet):
    permission_classes = [IsAdminOrDenyPolicy]
    serializer_class = StorageUserSerializer

    def get_queryset(self) -> QuerySet:
        storage = get_object_or_404(Storage.objects.all(), id=self.kwargs['storage_id'])
        queryset = StorageUser.objects.filter(storage=storage)

        return queryset

    def create(self, request: Request, *args, **kwargs) -> Response:
        storage = get_object_or_404(Storage.objects.all(), id=self.kwargs['storage_id'])
        request.data['storage'] = str(storage.id)

        return super(StorageUserViewSet, self).create(request=request, *args, **kwargs)
