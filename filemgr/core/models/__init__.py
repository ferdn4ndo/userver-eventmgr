from django.db.models import QuerySet

from core.exceptions.model_not_found_exception import ModelNotFoundException
from core.models.storage.storage_media_model import StorageMedia
from core.models.storage.storage_media_document_model import StorageMediaDocument
from core.models.storage.storage_media_image_model import StorageMediaImage
from core.models.storage.storage_media_image_sized_model import StorageMediaImageSized
from core.models.storage.storage_media_video_model import StorageMediaVideo
from core.models.storage.storage_model import Storage
from core.models.storage.storage_file_model import StorageFile
from core.models.storage.storage_file_download_model import StorageFileDownload
from core.models.storage.storage_file_mime_type_model import StorageFileMimeType
from core.models.storage.storage_user_model import StorageUser
from core.models.user.user_model import CustomUser
from core.models.user.user_token_model import UserToken


def get_object_or_not_found_error(queryset: QuerySet, *args, **kwargs):
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise ModelNotFoundException
