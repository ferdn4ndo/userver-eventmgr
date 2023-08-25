from rest_framework.permissions import BasePermission

from core.services.user.user_permission_service import UserPermissionService


class IsAdminOrDenyPolicy(BasePermission):
    """
    Object-level permission to only allow admins to read/write it.
    Assumes the model instance has an `created_by` attribute.
    """
    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True

        service = UserPermissionService(user=request.user)

        return service.is_admin()
