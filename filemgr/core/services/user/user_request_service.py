from django.utils import timezone
from rest_framework.request import Request

from core.models import CustomUser


class UserRequestService:
    request: Request
    user: CustomUser

    def __init__(self, request: Request):
        self.request = request
        self.user = self.request.user

    def prepare_create_audit_fields(self):
        if 'updated_at' in self.request.data:
            del(self.request.data['updated_at'])

        if 'updated_by' in self.request.data:
            del(self.request.data['updated_by'])

        self.request.data['created_at'] = timezone.now()
        self.request.data['created_by'] = self.request.user.id

    def prepare_update_audit_fields(self):
        if 'created_at' in self.request.data:
            del(self.request.data['created_at'])

        if 'created_by' in self.request.data:
            del(self.request.data['created_by'])

        self.request.data['updated_at'] = timezone.now()
        self.request.data['updated_by'] = self.request.user.id
