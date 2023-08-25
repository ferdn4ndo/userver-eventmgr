from django.db.models import QuerySet
from rest_framework.request import Request
from rest_framework.response import Response

from api.models import get_object_or_404
from api.policies.is_logged_in_policy import IsLoggedInPolicy
from api.services.storage.storage_file_view_service import StorageFileViewService
from api.views.generic_read_destroy_model_view import GenericReadDestroyModelViewSet
from core.models import Storage, StorageFile


class StorageTrashViewSet(GenericReadDestroyModelViewSet):
    permission_classes = [IsLoggedInPolicy]

    def get_queryset(self) -> QuerySet:
        storage = get_object_or_404(Storage.objects.all(), id=self.kwargs['storage_id'])
        queryset = StorageFile.create_storage_queryset(
            user=self.request.user,
            storage=storage,
            excluded=True,
        )

        return queryset

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        storage_file = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])

        service = StorageFileViewService()

        return service.delete_storage_file(storage_file=storage_file, user=request.user, soft_delete=False)
