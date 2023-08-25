from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from api.exceptions.bad_request_exception import BadRequestException
from api.exceptions.conflict_exception import ConflictException
from api.exceptions.permission_denied_exception import PermissionDeniedException
from api.serializers.storage.storage_file_serializer import StorageFileSerializer
from api.serializers.storage.storage_file_upload_from_file_serializer import StorageFileUploadFromFileSerializer
from api.serializers.storage.storage_file_upload_from_url_serializer import StorageFileUploadFromUrlSerializer
from core.models import Storage, StorageUser, StorageFile
from core.services.storage.storage_service import StorageService
from core.services.translation.translation_service import Messages
from core.services.user.user_permission_service import UserPermissionService


class StorageFileUploadViewService:
    @staticmethod
    def upload_from_request_file(request: Request, storage: Storage):
        if 'file' not in request.FILES:
            raise BadRequestException(Messages.MSG_MISSING_FILE_FIELD_FORM)
        request_file = request.FILES['file']

        permission_service = UserPermissionService(user=request.user)
        if not permission_service.is_admin() and not StorageUser.user_may_write_storage(request.user, storage):
            raise PermissionDeniedException(Messages.MSG_NO_STORAGE_WRITE_PERM)

        serializer = StorageFileUploadFromFileSerializer(data=request.POST)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = StorageService(storage=storage)
        driver = service.load_driver()

        try:
            storage_file = driver.upload_from_request_file(
                user=request.user,
                request_file=request_file,
                name=data['name'] if 'name' in data else '',
                visibility=data['visibility'] if 'visibility' in data else StorageFile.FileVisibility.USER,
                virtual_path=data['virtual_path'],
                overwrite=data['overwrite'] if 'overwrite' in data else False,
            )
        except FileExistsError:
            raise ConflictException(Messages.MGS_FILE_EXISTS_NO_OVERWRITE)

        file_serializer = StorageFileSerializer(storage_file)

        return Response(file_serializer.data, status.HTTP_201_CREATED)

    @staticmethod
    def upload_from_url(request: Request, storage: Storage):
        permission_service = UserPermissionService(user=request.user)
        if not permission_service.is_admin() and not StorageUser.user_may_write_storage(request.user, storage):
            raise PermissionDeniedException(Messages.MSG_NO_STORAGE_WRITE_PERM)

        serializer = StorageFileUploadFromUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        service = StorageService(storage=storage)
        driver = service.load_driver()

        try:
            storage_file = driver.upload_from_path(
                user=request.user,
                path=data['url'],
                name=data['name'] if 'name' in data else '',
                visibility=data['visibility'] if 'visibility' in data else StorageFile.FileVisibility.USER,
                virtual_path=data['virtual_path'],
                overwrite=data['overwrite'] if 'overwrite' in data else False,
                is_url=True,
            )
        except FileExistsError:
            raise ConflictException(Messages.MGS_FILE_EXISTS_NO_OVERWRITE)

        file_serializer = StorageFileSerializer(storage_file)

        return Response(file_serializer.data, status.HTTP_201_CREATED)
