from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import CustomUser


class UserToken(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, verbose_name=_("User that has the token"))
    token = models.CharField(
        max_length=255,
        unique=True,
        editable=False,
        verbose_name=_("Token used to login (from uServer-Auth)")
    )
    issued_at = models.DateTimeField(
        verbose_name="Date when the token was issued by uServer-Auth",
        editable=False
    )
    expires_at = models.DateTimeField(
        verbose_name="Date when the token expires (defined by uServer-Auth)",
        editable=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date when the token was registered for use by the serivice")
    )
