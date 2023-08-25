from __future__ import annotations

from json import JSONEncoder

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Storage(models.Model):
    """
    Model resource for a storage
    """

    class StorageType(models.TextChoices):
        """
        Enum for the type of storage
        """
        STORAGE_S3 = 'AMAZON_S3', _('Amazon S3')
        STORAGE_LOCAL = 'LOCAL', _('Local')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, choices=StorageType.choices, null=True)
    credentials = models.JSONField(
        max_length=1024,
        verbose_name=_("JSON containing the credentials used for connection"),
        encoder=JSONEncoder
    )
    media_convert_configuration = models.JSONField(
        max_length=1024,
        null=True,
        verbose_name=_("JSON containing the configuration used for converting media files"),
        encoder=JSONEncoder
    )
