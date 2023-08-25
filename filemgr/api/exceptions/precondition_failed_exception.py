from rest_framework import status

from api.exceptions.base_api_exception import BaseApiException
from core.services.translation.translation_service import Messages


class PreconditionFailedException(BaseApiException):
    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_detail = Messages.MSG_PRECONDITION_FAILED
    default_code = 'precondition_failed'
