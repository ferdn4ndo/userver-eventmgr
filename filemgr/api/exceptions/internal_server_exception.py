from rest_framework import status

from api.exceptions.base_api_exception import BaseApiException
from core.services.translation.translation_service import Messages


class InternalServerException(BaseApiException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = Messages.MSG_INTERNAL_ERROR
    default_code = 'internal_server_error'
