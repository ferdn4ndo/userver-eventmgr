from rest_framework.exceptions import APIException

from core.exceptions.base_core_exception import BaseCoreException
from core.services.translation.translation_service import Messages


class BaseApiException(BaseCoreException, APIException):
    detail: str
    default_detail = Messages.MSG_INTERNAL_ERROR

    def __init__(self, detail: str = ""):
        self.detail = detail

        if self.detail == "":
            self.detail = self.default_detail

    def __str__(self):
        return str(self.detail)
