from rest_framework import status

from api.exceptions.base_api_exception import BaseApiException
from core.services.translation.translation_service import Messages


class PermissionDeniedException(BaseApiException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = Messages.MSG_NOT_ENOUGH_PERMS
    default_code = 'permission_denied'
