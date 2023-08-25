from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models.generic_model import GenericModel


class StorageFileMimeType(GenericModel):
    """
    Stores the different possible mime types with their description, extension and a generic type enum
    """

    class GenericTypes(models.TextChoices):
        """
        Enum for the file type field
        """
        TEXT = 'TEXT', _('Text')
        FONT = 'FONT', _('Font')
        CODE = 'CODE', _('Code')
        EXECUTABLE = 'EXECUTABLE', _('Executable')
        AUDIO = 'AUDIO', _('Audio')
        IMAGE = 'IMAGE', _('Image')
        VIDEO = 'VIDEO', _('Video')
        COMPRESSED = 'COMPRESSED', _('Compressed')
        DOCUMENT = 'DOCUMENT', _('Document')
        BINARY = 'BINARY', _('Binary')
        OTHER = 'OTHER', _('Other')

    mime_type = models.CharField(max_length=255, unique=True)
    generic_type = models.CharField(max_length=50, choices=GenericTypes.choices, null=True)
    description = models.CharField(
        max_length=255,
        verbose_name=_("Description of the mime-type"),
        null=True,
    )
    extensions = models.CharField(
        max_length=255,
        verbose_name=_("Comma-separated list of the extensions of this mime (eg.: csv,xls,xlsx)"),
        null=True,
    )

    @staticmethod
    def from_mime_type(mime: str) -> [StorageFileMimeType]:
        """
        Returns a StorageFileMimeType object from a given mime-type string
        :param mime:
        :return:
        """
        mime = str(mime).strip().lower()
        if mime == "":
            return None

        # in case it's coming raw from the header, like 'text/html; charset=UTF-8'
        if ";" in mime:
            mime = mime.split(";")[0]

        mime, created = StorageFileMimeType.objects.get_or_create(mime_type=mime)
        mime.save()

        return mime
