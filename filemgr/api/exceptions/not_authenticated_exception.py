from rest_framework import status

from api.exceptions.base_api_exception import BaseApiException
from core.services.translation.translation_service import Messages


class NotAuthenticatedException(BaseApiException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = Messages.MSG_NOT_AUTHENTICATED
    default_code = 'not_authenticated'
