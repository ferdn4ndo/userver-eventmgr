from rest_framework.permissions import BasePermission, SAFE_METHODS

from core.services.user.user_permission_service import UserPermissionService


class IsStaffOrReadOnlyPolicy(BasePermission):
    """ Object-level permission to only allow everybody to read an object, but only staff can update it. """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        service = UserPermissionService(user=request.user)

        return service.is_admin_or_staff()
