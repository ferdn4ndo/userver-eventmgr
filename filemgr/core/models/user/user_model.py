from uuid import uuid4

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where uuid is the unique identifiers
    for authentication instead of usernames and tokens are the
    passwords.
    """
    def create_user(self, uuid, token, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not uuid:
            raise ValueError(_("The uuid must be set"))
        if not token:
            raise ValueError(_("The token must be set"))
        user = self.model(uuid=uuid, token=token, **extra_fields)
        user.set_password(token)
        user.save()
        return user

    def create_superuser(self, uuid, token, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(uuid, token, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Users within the uServer authentication system are represented by this model.
    UUID is required. Other fields are optional.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    username = models.CharField(max_length=32, verbose_name=_("Username of the user"))
    system_name = models.CharField(max_length=255, verbose_name=_("System name of the user"))
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Record creation timestamp"))
    last_activity_at = models.DateTimeField(
        verbose_name=_("Last activity registered by the user in the system"),
        default=timezone.now
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Record last update timestamp"))

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        """
        String representation of the model, defined by the UUID
        """
        return str(self.id)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
