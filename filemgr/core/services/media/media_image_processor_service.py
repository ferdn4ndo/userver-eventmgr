import os.path
import tempfile
from pathlib import Path

import math
from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageFont
from django.forms import model_to_dict

from api.settings import BASE_DIR
from core.models import StorageFile, StorageMediaImage, StorageMedia, StorageMediaImageSized
from core.models.storage.storage_media_thumbnail_model import StorageMediaThumbnail
from core.services.file.file_service import FileService
from core.services.image.image_overlay_service import ImageOverlayService
from core.services.logger.logger_service import get_logger
from core.services.media.media_image_service import MediaImageService
from core.services.message_broker.message_broker_service import MessageBrokerService
from core.services.storage.storage_file_service import StorageFileService


class MediaImageProcessorService:
    QUALITY_IMAGE_RESIZED=90
    QUALITY_IMAGE_THUMBNAIL=75

    def __init__(self, storage_file: StorageFile):
        self.logger = get_logger(__name__)
        self.storage_file = storage_file

        self._open_image()
        self._compute_hash()

        self.media_convert_configuration = self.storage_file.storage.media_convert_configuration

        self.media = self._create_storage_media()
        self.media_image = self._create_storage_media_image(storage_media=self.media)

    def _open_image(self):
        self.driver = StorageFileService(storage_file=self.storage_file).load_driver()

        self.temp_file_path = self.storage_file.get_temp_file_path()
        if not os.path.isfile(self.temp_file_path):
            self.driver.download_to_path(file=self.storage_file, local_path=self.temp_file_path)

        with Image.open(self.temp_file_path) as image:
            self.original_width, self.original_height = image.size

    def _compute_hash(self):
        self.storage_file.hash = FileService(filepath=self.temp_file_path).get_file_hash()
        self.storage_file.save()

    def _create_storage_media(self) -> StorageMedia:
        storage_media = StorageMedia(
            title=self.storage_file.name,
            type=StorageMedia.MediaType.IMAGE,
            description="",
            storage_file=self.storage_file,
            created_by=self.storage_file.created_by,
            updated_by=self.storage_file.updated_by,
        )
        storage_media.save()

        return storage_media

    def _create_storage_media_image(self, storage_media: StorageMedia) -> StorageMediaImage:
        media_image = StorageMediaImage(
            media=storage_media,
            size_tag=self.get_size_tag_from_dimensions(width=self.original_width, height=self.original_height),
            height=self.original_height,
            width=self.original_width,
            megapixels=(self.original_width * self.original_height)/1000000,
            created_by=self.storage_file.created_by,
            updated_by=self.storage_file.updated_by,
        )
        media_image.save()

        return media_image

    def process(self):
        self.logger.info(f"Processing image from storage file {self.storage_file.id}...")

        self.storage_file.status = StorageFile.FileStatus.PROCESSING
        self.storage_file.save()

        MessageBrokerService().send_message(
            topic='storage_file_processing_started',
            payload=model_to_dict(self.storage_file)
        )

        media_image_service = MediaImageService(media_image=self.media_image)
        media_image_service.update_file_metadata_from_path(image_path=self.temp_file_path)

        for image_size in self.media_convert_configuration["image_resizer"]["sizes"]:
            size_tag_width, size_tag_height = map(int, str(image_size).split("x"))
            self._process_image_size(size_tag_width=size_tag_width, size_tag_height=size_tag_height)

        self.logger.info(f"Creating thumbnails for file {self.storage_file.id}...")
        self.create_thumbnails()

        self.logger.info(f"Finished processing file {self.storage_file.id}!")

        self.storage_file.status = StorageFile.FileStatus.PUBLISHED
        self.storage_file.save()

        MessageBrokerService().send_message(
            topic='storage_file_processing_finished',
            payload=model_to_dict(self.storage_file)
        )

    def _process_image_size(self, size_tag_width: int, size_tag_height: int):
        resize_width, resize_height = self.compute_new_image_dimensions(expected_width=size_tag_width, expected_height=size_tag_height)
        if self.original_width < resize_width or self.original_height < resize_height:
            self.logger.warning(
                f"Skipping the resize of media_image ID {self.media_image.id} for the dimensions"
                f" {resize_width} x {resize_height} [WxH] as the original image is smaller"
                f" ({self.original_width} x {self.original_height})"
            )
            return

        size_tag = self.get_size_tag_from_dimensions(width=resize_width, height=resize_height)

        with Image.open(self.temp_file_path) as image:
            resized_image = image.resize((resize_width, resize_height), Image.ANTIALIAS)

            ImageOverlayService(
                configuration=self.media_convert_configuration,
                image=resized_image,
                metadata=self.storage_file.custom_metadata,
            ).add_overlay()

            self.save_resized_image(
                size_tag=size_tag,
                width=resize_width,
                height=resize_height,
                image=resized_image,
                quality=self.QUALITY_IMAGE_RESIZED,
            )

    def compute_new_image_dimensions(self, expected_width: int, expected_height: int) -> tuple:
        size_factor = expected_width/self.original_width if self.original_height > self.original_width else expected_height/self.original_height

        return round(self.original_width * size_factor), round(self.original_height * size_factor)

    def create_resized_file_resource(self) -> StorageFile:
        resized_storage_file = self.driver.create_empty_file_resource(user=self.storage_file.created_by)
        resized_storage_file.owner = self.storage_file.owner
        resized_storage_file.exif_metadata = self.storage_file.exif_metadata
        resized_storage_file.custom_metadata = self.storage_file.custom_metadata
        resized_storage_file.name = self.storage_file.name
        resized_storage_file.original_path = self.storage_file.original_path
        resized_storage_file.visibility = self.storage_file.visibility

        return resized_storage_file

    def create_thumbnails(self):
        thumbnail_sizes = [
            {
                "tag": StorageMedia.MediaSizeTag.SIZE_THUMB_LARGE,
                "width": 960,
                "height": 720,
            },
            {
                "tag": StorageMedia.MediaSizeTag.SIZE_THUMB_MEDIUM,
                "width": 480,
                "height": 360,
            },
            {
                "tag": StorageMedia.MediaSizeTag.SIZE_THUMB_SMALL,
                "width": 240,
                "height": 180,
            },
        ]

        for thumbnail_params in thumbnail_sizes:
            self.create_thumbnail(
                size_tag=thumbnail_params["tag"],
                width=thumbnail_params["width"],
                height=thumbnail_params["height"],
            )

        self.logger.info(f"FINISHED CREATING THUMBNAILS FOR FILE ID {self.storage_file.id}")

    @staticmethod
    def _get_center_box(outer_width: int, outer_height: int, inner_width: int, inner_height: int) -> tuple:
        left = math.floor((outer_width - inner_width)/2)
        top = math.floor((outer_height - inner_height)/2)
        right = math.floor((outer_width + inner_width)/2)
        bottom = math.floor((outer_height + inner_height)/2)

        return left, top, right, bottom

    def save_resized_image(
            self,
            size_tag: str,
            width: int,
            height: int,
            image: Image.Image,
            quality: int = QUALITY_IMAGE_RESIZED,
    ):
        resized_file_folder = os.path.join(tempfile.gettempdir(), "resized", size_tag)
        Path(resized_file_folder).mkdir(parents=True, exist_ok=True)
        resized_file_path = os.path.join(resized_file_folder, str(self.storage_file.id))
        image.save(fp=resized_file_path, format="JPEG", quality=quality)

        thumbnail_storage_file = self.driver.perform_basic_upload_operations(
            user=self.storage_file.owner,
            path=resized_file_path,
            name=self.storage_file.name,
            virtual_path=f"resized/{size_tag}/{self.storage_file.virtual_path}",
            original_path=self.storage_file.original_path,
            origin=StorageFile.FileOrigin.SYSTEM,
            overwrite=True,
            visibility=self.storage_file.visibility,
            is_url=False,
            size_tag=size_tag,
        )

        thumbnail_storage_file.exif_metadata = self.storage_file.exif_metadata
        thumbnail_storage_file.custom_metadata = self.storage_file.custom_metadata
        thumbnail_storage_file.status = StorageFile.FileStatus.PUBLISHED
        thumbnail_storage_file.save()

        thumbnail_size_tags = [
            StorageMedia.MediaSizeTag.SIZE_THUMB_LARGE,
            StorageMedia.MediaSizeTag.SIZE_THUMB_MEDIUM,
            StorageMedia.MediaSizeTag.SIZE_THUMB_SMALL,
        ]

        if size_tag in thumbnail_size_tags:
            media_thumbnail = StorageMediaThumbnail(
                media=self.media,
                storage_file=thumbnail_storage_file,
                size_tag=size_tag,
                height=height,
                width=width,
                megapixels=(width * height)/1000000,
                created_by=self.storage_file.created_by,
                updated_by=self.storage_file.updated_by,
            )
            media_thumbnail.save()
        else:
            media_image_sized = StorageMediaImageSized(
                media_image=self.media_image,
                storage_file=thumbnail_storage_file,
                size_tag=size_tag,
                height=height,
                width=width,
                megapixels=(width * height)/1000000,
                created_by=self.storage_file.created_by,
                updated_by=self.storage_file.updated_by,
            )
            media_image_sized.save()

        self.logger.info(
            f"Finished resizing file {self.storage_file.id} to size {width} x {height} (tmp path: {resized_file_path})"
        )

    def create_thumbnail(self, size_tag: str, width: int, height: int):
        thumbnail_image = Image.new("RGB", (width, height))

        original_proportion = round(self.original_width/self.original_height, 2)
        thumbnail_proportion = round(width/height, 2)
        if thumbnail_proportion != original_proportion:
            self.logger.info("ADJUSTING THUMBNAIL BACKGROUND")
            background_width, background_height = self.compute_new_image_dimensions(expected_width=width, expected_height=height)
            image = Image.open(fp=self.temp_file_path)
            image.thumbnail((background_width, background_height))

            image = image.crop(self._get_center_box(
                outer_width=background_width,
                outer_height=background_height,
                inner_width=width,
                inner_height=height,
            ))
            image = image.filter(ImageFilter.BoxBlur(radius=5))
            image = ImageOps.grayscale(image)
            thumbnail_image.paste(image)

        image = Image.open(fp=self.temp_file_path)
        image.thumbnail((width, height))
        image_width, image_height = image.size

        thumbnail_image.paste(image, self._get_center_box(
            outer_width=width,
            outer_height=height,
            inner_width=image_width,
            inner_height=image_height,
        ))

        self.save_resized_image(
            size_tag=size_tag,
            width=width,
            height=height,
            image=thumbnail_image,
            quality=self.QUALITY_IMAGE_THUMBNAIL,
        )

    @staticmethod
    def get_size_tag_from_dimensions(width: int, height: int):
        if width >= 8192 and height >= 5472:
            return StorageMedia.MediaSizeTag.SIZE_8K

        if width >= 4096 and height >= 2752:
            return StorageMedia.MediaSizeTag.SIZE_4K

        if width >= 3200 and height >= 2144:
            return StorageMedia.MediaSizeTag.SIZE_3K

        if width >= 2048 and height >= 1376:
            return StorageMedia.MediaSizeTag.SIZE_2K

        if width >= 1280 and height >= 864:
            return StorageMedia.MediaSizeTag.SIZE_1K

        return StorageMedia.MediaSizeTag.SIZE_VGA
