from api.policies.is_admin_or_deny_policy import IsAdminOrDenyPolicy
from api.serializers.storage.storage_serializer import StorageSerializer
from api.views.generic_crud_with_list_model_view import GenericCrudWithListModelViewSet
from core.models import Storage


class StorageViewSet(GenericCrudWithListModelViewSet):
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer
    permission_classes = [IsAdminOrDenyPolicy]
