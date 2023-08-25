from __future__ import annotations

import os
import re
import tempfile
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from core.models.generic_audited_model import GenericAuditedModel
from core.services.strings.strings_service import StringsService
from core.services.translation.translation_service import Messages

from core.models.storage.storage_file_mime_type_model import StorageFileMimeType
from core.models.storage.storage_model import Storage
from core.models.user.user_model import CustomUser



class StorageFile(GenericAuditedModel):
    """
    StorageFile resource model
    """

    class FileStatus(models.TextChoices):
        """
        Enum for the file status field
        """
        NOT_UPLOADED = 'NOT_UPLOADED', _('The file upload has not started yet.')
        UPLOADING = 'UPLOADING', _('The file is being uploaded.')
        UPLOADED = 'UPLOADED', _('The file was uploaded and is waiting to enter the processing queue (or skipped).')
        QUEUED = 'QUEUED', _('The file needs post processing and is waiting in the queue.')
        PROCESSING = 'PROCESSING', _('The file is being post processed.')
        PUBLISHED = 'PUBLISHED', _('The file upload and post processing was completed and the file is ready.')
        DELETED = 'DELETED', _('The file was deleted.')
        ERROR = 'ERROR', _('An error occurred during one of the steps.')

    class FileVisibility(models.TextChoices):
        """
        Enum for the file visibility field
        """
        PUBLIC = 'PUBLIC', _('Public')
        SYSTEM = 'SYSTEM', _('System')
        USER = 'USER', _('User')

    class FileOrigin(models.TextChoices):
        """
        Enum for the file origin field. Local for raw uploaded files and web for remote downloaded ones.
        """
        LOCAL = 'LOCAL', _('Local')
        WEB = 'WEB', _('Web')
        SYSTEM = 'SYSTEM', _('System')
        UNKNOWN = 'UNKNOWN', _('Unknown')

    signature_key = models.CharField(max_length=64, default=StringsService.generate_random_encoded_string)
    storage = models.ForeignKey(to=Storage, on_delete=models.CASCADE, editable=False)
    owner = models.ForeignKey(to=CustomUser, on_delete=models.SET_NULL, null=True, related_name="storage_file_owner")
    name = models.CharField(max_length=255, verbose_name=_("A name for the file"), null=True)
    status = models.CharField(max_length=50, choices=FileStatus.choices, default=FileStatus.NOT_UPLOADED)
    visibility = models.CharField(max_length=50, choices=FileVisibility.choices, default=FileVisibility.SYSTEM)
    size = models.BigIntegerField(verbose_name=_("File size in bytes"), default=0)
    hash = models.CharField(max_length=255, null=True, verbose_name=_("Hash of the processed file"))
    type = models.ForeignKey(to=StorageFileMimeType, on_delete=models.SET_NULL, null=True)
    extension = models.CharField(max_length=16, null=True, verbose_name=_("Extension of the file"))
    exif_metadata = models.JSONField(default=dict, null=True, verbose_name=_("Dict with the file exif metadata"))
    custom_metadata = models.JSONField(default=dict, null=True, verbose_name=_("Dict with the metadata of the integrated system"))
    origin = models.CharField(max_length=255, choices=FileOrigin.choices, default=FileOrigin.UNKNOWN)
    original_path = models.CharField(
        max_length=1024,
        null=True,
        verbose_name=_("Either the original URL of the file (if remotely downloaded) or the file path (if uploaded)"),
    )
    real_path = models.CharField(
        max_length=1024,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\/?([\w\.\_-]+\/)*[\w\.\_-]+$',
                message=Messages.MGS_INVALID_PATH,
                code='invalid_filepath',
                flags=re.UNICODE,
            )
        ],
        verbose_name=_("The real remote filepath of the stored file"),
    )
    virtual_path = models.CharField(
        max_length=1024,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\/?([\w\.\_-]+\/)*[\w\.\_-]+$',
                message=Messages.MGS_INVALID_PATH,
                code='invalid_filepath',
                flags=re.UNICODE,
            ),
        ],
        verbose_name=_("The virtual remote filepath of the stored file"),
    )
    available = models.BooleanField(default=True, verbose_name=_("If the file is remotely available"))
    excluded = models.BooleanField(default=False, verbose_name=_("If the file was marked as excluded in the interface"))
    # download_url =
    # download_url_expires_at =

    def get_temp_file_path(self) -> str:
        """
        Retrieve a local temp path for the file
        :return: the temp file path
        """
        return os.path.join(tempfile.gettempdir(), str(self.id))

    def get_filename_from_virtual_path(self):
        """
        Retrieves the filename base on the file virtual path (last part of a '/' explosion)
        :return:
        """
        return str(self.virtual_path).split("/")[-1]

    def is_visible_by_user(self, user: CustomUser) -> bool:
        """
        Retrieves a boolean indicating whether the file is visible to a given user or not
        :param user:
        :return:
        """
        return (
            (self.visibility == StorageFile.FileVisibility.USER and self.owner == user) or
            (self.visibility == StorageFile.FileVisibility.SYSTEM and self.owner.system_name != user.system_name) or
            (self.visibility == StorageFile.FileVisibility.PUBLIC)
        )

    @staticmethod
    def create_storage_queryset(user: CustomUser, storage: Storage, excluded: bool = False):
        queryset = StorageFile.objects.filter(storage=storage, excluded=excluded)

        if user.is_admin:
            return queryset

        queryset.filter(storage=storage).filter(
            Q(visibility=StorageFile.FileVisibility.PUBLIC) |
            (
                Q(visibility=StorageFile.FileVisibility.SYSTEM) &
                Q(owner__system_name=user.system_name)
            ) |
            (
                Q(visibility=StorageFile.FileVisibility.USER) &
                Q(owner=user)
            )
        )

        return queryset
