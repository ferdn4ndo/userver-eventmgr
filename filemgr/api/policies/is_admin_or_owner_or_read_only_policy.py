from rest_framework.permissions import BasePermission, SAFE_METHODS

from core.services.user.user_permission_service import UserPermissionService


class IsAdminOrOwnerOrReadOnlyPolicy(BasePermission):
    """
    Object-level permission to only allow everybody to read an object, but only admins or creators to update it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        service = UserPermissionService(user=request.user)

        # Instance must have an attribute named `owner`.
        return service.is_admin() or obj.owner == request.user
