from rest_framework import status

from api.exceptions.base_api_exception import BaseApiException
from core.services.translation.translation_service import Messages


class NotFoundException(BaseApiException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = Messages.MSG_NOT_FOUND
    default_code = 'not_found'
