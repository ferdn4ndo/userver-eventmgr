from rest_framework import mixins

from api.views.generic_model_update_mixin import GenericModelUpdateMixin
from api.views.generic_model_view import GenericModelViewSet


class GenericReadUpdateDestroyModelViewSet(mixins.RetrieveModelMixin,
                                    mixins.ListModelMixin,
                                    GenericModelUpdateMixin,
                                    mixins.DestroyModelMixin,
                                    GenericModelViewSet):
    pass
