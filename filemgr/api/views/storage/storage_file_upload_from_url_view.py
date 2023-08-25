from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from api.services.policy import IsLoggedIn
from api.services.storage.storage_file_upload_view_service import StorageFileUploadViewService
from core.models import Storage


class StorageFileUploadUrlView(viewsets.ViewSet):
    permission_classes = [IsLoggedIn]

    def create(self, request: Request, storage_id: str) -> Response:
        storage = get_object_or_404(Storage.objects.all(), id=storage_id)
        service = StorageFileUploadViewService()

        return service.upload_from_url(request=request, storage=storage)
