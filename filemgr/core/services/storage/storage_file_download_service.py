from core.models import CustomUser


class StorageFileDownloadService:
    @staticmethod
    def check_file_download_permissions(self, user: CustomUser, storage_id: str, file_id: str):
        storage = get_object_or_404(Storage.objects.all(), id=storage_id)
        if not StorageUser.user_may_read_storage(request.user, storage):
            raise PermissionDeniedException(Messages.MSG_NO_STORAGE_READ_PERM)

        file = get_object_or_404(
            StorageFile.create_storage_queryset(user=request.user, storage=storage),
            id=kwargs['file_id']
        )
        if not file.is_visible_by_user(request.user):
            raise PermissionDeniedException(Messages.MSG_NO_FILE_DOWNLOAD_PERM)
