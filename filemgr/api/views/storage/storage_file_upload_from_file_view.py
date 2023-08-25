from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from api.policies.is_logged_in_policy import IsLoggedInPolicy
from api.services.storage.storage_file_upload_view_service import StorageFileUploadViewService
from core.models import Storage


@method_decorator(csrf_exempt, name='dispatch')
class StorageFileUploadView(viewsets.ViewSet):
    permission_classes = [IsLoggedInPolicy]

    def create(self, request: Request, storage_id: str) -> Response:
        storage = get_object_or_404(Storage.objects.all(), id=storage_id)
        service = StorageFileUploadViewService()

        return service.upload_from_request_file(request=request, storage=storage)
