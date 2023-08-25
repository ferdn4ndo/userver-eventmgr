from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response

from api.exceptions.permission_denied_exception import PermissionDeniedException
from core.models import StorageFile, CustomUser, StorageUser
from core.services.translation.translation_service import Messages


class StorageFileViewService:
    def check_file_permissions(self, storage_file: StorageFile, user: CustomUser, write: bool = False):
        if not write and not StorageUser.user_may_read_storage(user=user, storage=storage_file.storage):
            raise PermissionDeniedException(Messages.MSG_NO_STORAGE_READ_PERM)
        elif write and not StorageUser.user_may_write_storage(user=user, storage=storage_file.storage):
            raise PermissionDeniedException(Messages.MSG_NO_STORAGE_WRITE_PERM)

        if not storage_file.is_visible_by_user(user=user):
            raise PermissionDeniedException(Messages.MSG_NO_FILE_READ_PERM)

    @staticmethod
    def delete_storage_file(storage_file: StorageFile, user: CustomUser, soft_delete: bool = True) -> Response:
        if soft_delete:
            storage_file.excluded = True
            storage_file.created_at = timezone.now()
            storage_file.created_by = user.id
            storage_file.save()

        else:
            storage_file.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
