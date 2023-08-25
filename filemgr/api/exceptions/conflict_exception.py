from rest_framework import status

from api.exceptions.base_api_exception import BaseApiException
from core.services.translation.translation_service import Messages


class ConflictException(BaseApiException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = Messages.MSG_CONFLICT
    default_code = 'conflict'
