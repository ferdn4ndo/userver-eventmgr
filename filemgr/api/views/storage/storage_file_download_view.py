from django.http import JsonResponse
from django.utils import timezone
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request

from api.policies.is_logged_in_policy import IsLoggedInPolicy
from api.serializers.storage.storage_file_download_serializer import StorageFileDownloadSerializer
from api.services.storage.storage_file_download_view_service import StorageFileDownloadViewService
from api.views.generic_create_read_model_view import GenericCreateReadModelViewSet
from core.models import StorageFileDownload, StorageFile, Storage


class StorageFileDownloadViewSet(GenericCreateReadModelViewSet):
    permission_classes = [IsLoggedInPolicy]
    serializer_class = StorageFileDownloadSerializer

    def get_queryset(self):
        storage = get_object_or_404(Storage.objects.all(), id=self.kwargs['storage_id'])
        storage_file = get_object_or_404(
            StorageFile.create_storage_queryset(user=self.request.user, storage=storage),
            id=self.kwargs['file_id']
        )
        queryset = StorageFileDownload.objects.filter(
            owner=self.request.user,
            storage_file=storage_file,
            expires_at__gte=timezone.now(),
        )

        return queryset

    def create(self, request: Request, *args, **kwargs) -> JsonResponse:
        return StorageFileDownloadViewService.create_download_link_from_request(
            request=request,
            storage_id=self.kwargs['storage_id'],
            file_id=self.kwargs['file_id'],
        )
