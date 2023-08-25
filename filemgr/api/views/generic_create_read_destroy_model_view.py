from rest_framework import mixins

from api.views.generic_model_create_mixin import GenericModelCreateMixin
from api.views.generic_model_view import GenericModelViewSet


class GenericCreateReadDestroyModelViewSet(GenericModelCreateMixin,
                                    mixins.RetrieveModelMixin,
                                    mixins.ListModelMixin,
                                    mixins.DestroyModelMixin,
                                    GenericModelViewSet):
    pass
