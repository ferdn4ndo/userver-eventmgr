from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models.generic_audited_model import GenericAuditedModel
from core.models.storage.storage_media_model import StorageMedia
from core.models.storage.storage_media_image_model import StorageMediaImage
from core.models.storage.storage_file_model import StorageFile


class StorageMediaImageSized(GenericAuditedModel):

    media_image = models.ForeignKey(to=StorageMediaImage, on_delete=models.CASCADE, editable=False, related_name="sized_images")
    storage_file = models.OneToOneField(to=StorageFile, on_delete=models.CASCADE, editable=False)
    size_tag = models.CharField(max_length=64, choices=StorageMedia.MediaSizeTag.choices, null=True)
    height = models.PositiveIntegerField(verbose_name=_("Height of the sized media item"), null=True)
    width = models.PositiveIntegerField(verbose_name=_("Width of the sized media item"), null=True)
    megapixels = models.DecimalField(
        verbose_name="Total millions of pixels (h x w) of the image",
        max_digits=7,
        decimal_places=4,
        null=True,
    )


class StorageMediaImageSizedAdmin(admin.ModelAdmin):
    pass


admin.site.register(StorageMediaImageSized, StorageMediaImageSizedAdmin)
