from rest_framework import mixins

from api.views.generic_model_view import GenericModelViewSet


class GenericReadModelViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       GenericModelViewSet):
    pass
