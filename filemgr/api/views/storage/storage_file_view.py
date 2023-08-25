from django.db.models import QuerySet
from rest_framework.request import Request
from rest_framework.response import Response

from api.models import get_object_or_404
from api.policies.is_admin_or_owner_or_read_only_policy import IsAdminOrOwnerOrReadOnlyPolicy
from api.policies.is_logged_in_policy import IsLoggedInPolicy
from api.serializers.storage.storage_file_serializer import StorageFileSerializer
from api.services.storage.storage_file_view_service import StorageFileViewService
from api.views.generic_read_update_destroy_model_view import GenericReadUpdateDestroyModelViewSet
from core.models import StorageFile, Storage, get_object_or_not_found_error
from core.services.media.media_file_service import MediaFileService


class StorageFileViewSet(GenericReadUpdateDestroyModelViewSet):
    permission_classes = [IsLoggedInPolicy, IsAdminOrOwnerOrReadOnlyPolicy]
    serializer_class = StorageFileSerializer

    def get_queryset(self) -> QuerySet:
        if getattr(self, "swagger_fake_view", False):
            # queryset just for schema generation metadata
            return StorageFile.objects.none()

        storage = get_object_or_not_found_error(Storage.objects.all(), id=self.kwargs['storage_id'])
        queryset = StorageFile.create_storage_queryset(user=self.request.user, storage=storage, excluded=False)

        return queryset

    def update(self, request: Request, *args, **kwargs) -> Response:
        response = super(StorageFileViewSet, self).update(request=request, *args, **kwargs)

        if 'custom_metadata' in request.data:
            service = MediaFileService(storage_file=self.get_object())
            service.process_if_is_media_file()

        return response

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        storage_file = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])

        service = StorageFileViewService()

        return service.delete_storage_file(storage_file=storage_file, user=request.user, soft_delete=True)
