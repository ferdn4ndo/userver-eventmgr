from django.contrib.auth.models import AnonymousUser

from core.models import CustomUser


class UserPermissionService:
    user: CustomUser

    def __init__(self, user: [CustomUser] = None):
        self.user = user

    def is_admin_or_staff(self) -> bool:
        return self.is_admin() or self.is_staff()

    def is_admin(self) -> bool:
        if not self.is_logged_in():
            return False

        return self.user.is_admin

    def is_staff(self) -> bool:
        if not self.is_logged_in():
            return False

        return self.user.is_staff

    def is_logged_in(self) -> bool:
         if self.user is None:
            return False

         return type(self.user) is not AnonymousUser
