from rest_framework import mixins

from api.views.generic_model_view import GenericModelViewSet


class GenericReadDestroyModelViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              GenericModelViewSet):
    pass
