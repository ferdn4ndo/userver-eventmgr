from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import StorageFile
from core.models.generic_audited_model import GenericAuditedModel
from core.models.storage.storage_media_model import StorageMedia


class StorageMediaThumbnail(GenericAuditedModel):

    media = models.ForeignKey(to=StorageMedia, on_delete=models.CASCADE, editable=False, related_name="thumbnails")
    storage_file = models.ForeignKey(to=StorageFile, on_delete=models.CASCADE, editable=False)
    size_tag = models.CharField(
        max_length=64,
        null=True,
        choices=StorageMedia.MediaSizeTag.choices,
        verbose_name=_("The size of the thumbnail.")
    )
    height = models.PositiveIntegerField(verbose_name=_("Height of the sized media item"), null=True)
    width = models.PositiveIntegerField(verbose_name=_("Width of the sized media item"), null=True)
    megapixels = models.DecimalField(
        verbose_name="Total millions of pixels (h x w) of the image",
        max_digits=7,
        decimal_places=4,
        null=True,
    )


class StorageMediaThumbnailAdmin(admin.ModelAdmin):
    pass


admin.site.register(StorageMediaThumbnail, StorageMediaThumbnailAdmin)
