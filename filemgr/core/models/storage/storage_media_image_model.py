from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models.generic_audited_model import GenericAuditedModel
from core.models.storage.storage_media_model import StorageMedia


class StorageMediaImage(GenericAuditedModel):

    media = models.OneToOneField(to=StorageMedia, on_delete=models.CASCADE, editable=False)
    focal_length = models.FloatField(null=True, verbose_name=_("Focal length of the lenses in millimeters"))
    aperture = models.CharField(max_length=255, null=True)
    flash_fired = models.BooleanField(null=True)
    iso = models.PositiveIntegerField(null=True)
    orientation_angle = models.IntegerField(null=True)
    is_flipped = models.BooleanField(null=True)
    exposition = models.CharField(max_length=255, null=True)
    datetime_taken = models.CharField(max_length=255, null=True)
    camera_manufacturer = models.CharField(max_length=255, null=True)
    camera_model = models.CharField(max_length=255, null=True)
    exif_image_height = models.IntegerField(null=True)
    exif_image_width = models.IntegerField(null=True)
    size_tag = models.CharField(
        max_length=64,
        null=True,
        choices=StorageMedia.MediaSizeTag.choices,
        verbose_name=_("Biggest size tag of the media item")
    )
    height = models.PositiveIntegerField(verbose_name="Height of the media item", null=True)
    width = models.PositiveIntegerField(verbose_name="Width of the media item", null=True)
    megapixels = models.DecimalField(
        verbose_name="Total millions of pixels (h x w) of the image",
        max_digits=7,
        decimal_places=4,
        null=True,
    )


class StorageMediaImageAdmin(admin.ModelAdmin):
    pass


admin.site.register(StorageMediaImage, StorageMediaImageAdmin)
