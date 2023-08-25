from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models.storage.storage_model import Storage
from core.models.generic_audited_model import GenericAuditedModel
from core.models.storage.storage_file_model import StorageFile
from core.models.user.user_model import CustomUser


class StorageMedia(GenericAuditedModel):

    class MediaType(models.TextChoices):
        DOCUMENT = 'DOCUMENT', _("The media item is a document.")
        IMAGE = 'IMAGE', _("The media item is an image.")
        VIDEO = 'VIDEO', _("The media item is a video.")

    class MediaSizeTag(models.TextChoices):
        """ To get the height from the width, use: math.ceil((Width*2/3)/32)*32 """
        SIZE_8K = 'SIZE_8K', _("8K (min 8192x5472 px @ 3:2, 45 Megapixels)")  # ~8K UHD
        SIZE_4K = 'SIZE_4K', _("4K (min 4096x2752 px @ 3:2, 11 Megapixels)")  # ~DCI 4K
        SIZE_3K = 'SIZE_3K', _("3K (min 3200x2144 px @ 3:2, 6.9 Megapixels)")  # ~QHD+
        SIZE_2K = 'SIZE_2K', _("2K (min 2048x1376 px @ 3:2, 2.8 Megapixels)")  # ~DCI 2K
        SIZE_1K = 'SIZE_1K', _("1K (min 1280x864 px @ 3:2, 1.1 Megapixels)")  # ~HD
        SIZE_VGA = 'SIZE_VGA', _("VGA (min 800x600 px @ 4:3, <1 Megapixel)")  # VGA
        SIZE_THUMB_LARGE = 'SIZE_THUMB_LARGE', _("Large Thumbnail [4:3] (960×720 px)")  # DVGA
        SIZE_THUMB_MEDIUM = 'SIZE_THUMB_MEDIUM', _("Medium Thumbnail [4:3] (480×360 px)")  # WQVGA
        SIZE_THUMB_SMALL = 'SIZE_THUMB_SMALL', _("Small Thumbnail [4:3] (240x180 px)")  # HQVGA

    title = models.CharField(max_length=255, null=True)
    type = models.CharField(
        max_length=64,
        choices=MediaType.choices,
        verbose_name=_("The type of the media item")
    )
    description = models.TextField(max_length=65535, null=True)
    storage_file = models.OneToOneField(to=StorageFile, on_delete=models.CASCADE, editable=False, related_name="media_file")

    @staticmethod
    def create_media_queryset(user: CustomUser, storage: Storage):
        queryset = StorageMedia.objects.filter(storage_file__storage=storage)

        if user.is_admin:
            return queryset

        return queryset.filter(storage_file__owner=user)


class StorageMediaAdmin(admin.ModelAdmin):
    pass


admin.site.register(StorageMedia, StorageMediaAdmin)
