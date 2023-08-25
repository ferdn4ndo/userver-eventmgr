from django.utils import timezone
from rest_framework import mixins
from rest_framework.request import Request
from rest_framework.response import Response


class GenericModelCreateMixin(mixins.CreateModelMixin):

    def create(self, request: Request, *args, **kwargs) -> Response:
        if 'updated_at' in request.data:
            del(request.data['updated_at'])

        if 'updated_by' in request.data:
            del(request.data['updated_by'])

        request.data['created_at'] = timezone.now()
        request.data['created_by'] = request.user.id

        return super(GenericModelCreateMixin, self).create(request=request, *args, **kwargs)
