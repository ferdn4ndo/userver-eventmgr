from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.throttling import UserRateThrottle


class DefaultUserThrottle(UserRateThrottle):
    # check https://stackoverflow.com/questions/34538695/django-rest-framework-per-user-throttles
    rate = '1000/day'


class AllowAll(BasePermission):
    def has_permission(self, request, view):
        return True


class IsLoggedIn(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True

        return bool(request.user and request.user.is_authenticated)


class IsAdminOrCreatorOrReadOnly(BasePermission):
    """
    Object-level permission to only allow everybody to read an object, but only admins or creators to update it.
    Assumes the model instance has an `created_by` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `created_by`.
        return request.user.is_admin or obj.created_by == request.user


class IsAdminOrOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow everybody to read an object, but only admins or creators to update it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return request.user.is_admin or obj.owner == request.user


class IsAdminOrCreatorOrDeny(BasePermission):
    """
    Object-level permission to only allow admins or creators of an object to read/write it.
    Assumes the model instance has an `created_by` attribute.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_admin or obj.created_by == request.user


class IsAdminOrOwnerOrDeny(BasePermission):
    """
    Object-level permission to only allow admins or creators of an object to read/write it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_admin or obj.owner == request.user


class IsAdminOrDeny(BasePermission):
    """
    Object-level permission to only allow admins to read/write it.
    Assumes the model instance has an `created_by` attribute.
    """
    def has_permission(self, request, view):
        return request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """ Object-level permission to only allow everybody to read an object, but only admins to update it. """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_admin
