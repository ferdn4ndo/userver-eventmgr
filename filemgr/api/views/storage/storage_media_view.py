from django.db.models import QuerySet

from api.models import get_object_or_404
from api.policies.is_admin_or_owner_or_read_only_policy import IsAdminOrOwnerOrReadOnlyPolicy
from api.policies.is_logged_in_policy import IsLoggedInPolicy
from api.serializers.storage.storage_media_serializer import StorageMediaSerializer
from api.views.generic_read_model_view import GenericReadModelViewSet
from core.models import StorageMedia, Storage


class StorageMediaViewSet(GenericReadModelViewSet):
    permission_classes = [IsLoggedInPolicy, IsAdminOrOwnerOrReadOnlyPolicy]
    serializer_class = StorageMediaSerializer

    def get_queryset(self) -> QuerySet:
        if getattr(self, "swagger_fake_view", False):
            # queryset just for schema generation metadata
            return StorageMedia.objects.none()

        storage = get_object_or_404(Storage.objects.all(), id=self.kwargs['storage_id'])

        return StorageMedia.create_media_queryset(storage=storage, user=self.request.user)
