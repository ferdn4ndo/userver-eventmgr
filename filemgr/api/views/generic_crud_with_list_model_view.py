from rest_framework import mixins

from api.views.generic_model_create_mixin import GenericModelCreateMixin
from api.views.generic_model_update_mixin import GenericModelUpdateMixin
from api.views.generic_model_view import GenericModelViewSet


class GenericCrudWithListModelViewSet(GenericModelCreateMixin,
                               mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,
                               GenericModelUpdateMixin,
                               mixins.DestroyModelMixin,
                               GenericModelViewSet):
    pass
