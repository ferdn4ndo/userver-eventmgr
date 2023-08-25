from django.utils import timezone
from rest_framework import mixins
from rest_framework.request import Request
from rest_framework.response import Response


class GenericModelUpdateMixin(mixins.UpdateModelMixin):

    def update(self, request: Request, *args, **kwargs) -> Response:
        if 'created_at' in request.data:
            del(request.data['created_at'])

        if 'created_by' in request.data:
            del(request.data['created_by'])

        request.data['updated_at'] = timezone.now()
        request.data['updated_by'] = request.user.id

        return super(GenericModelUpdateMixin, self).update(request=request, *args, **kwargs)
