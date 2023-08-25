from rest_framework import status

from api.exceptions.base_api_exception import BaseApiException
from core.services.translation.translation_service import Messages


class NoStorageWritePermissionException(BaseApiException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = Messages.MSG_NO_STORAGE_WRITE_PERM
    default_code = 'no_storage_write_perm'
