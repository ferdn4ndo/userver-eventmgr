from rest_framework.permissions import BasePermission


class AllowAllPolicy(BasePermission):
    def has_permission(self, request, view):
        return True
