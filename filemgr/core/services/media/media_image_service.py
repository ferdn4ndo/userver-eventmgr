from core.models.storage.storage_media_image_model import StorageMediaImage
from core.models.storage.storage_media_image_sized_model import StorageMediaImageSized
from core.services.photo.photo_exif_service import PhotoExifService


class MediaImageService:
    media_image: StorageMediaImage

    def __init__(self, media_image: StorageMediaImage):
        self.media_image = media_image

    def update_file_metadata_from_path(self, image_path: str) -> StorageMediaImage:
        service = PhotoExifService(file_path=image_path)

        self.media_image.height = service.get_image_height()
        self.media_image.width = service.get_image_width()
        self.media_image.focal_length = service.get_exif_focal_length()
        self.media_image.aperture = service.get_exif_aperture()
        self.media_image.iso = service.get_exif_data_by_key('ISOSpeedRatings')
        self.media_image.flash_fired = service.get_exif_flash_fired()
        self.media_image.orientation_angle = service.get_exif_orientation_angle()
        self.media_image.is_flipped = service.get_exif_orientation_is_flipped()
        self.media_image.exposition = service.get_exif_exposition()
        self.media_image.datetime_taken = service.get_exif_data_by_key('DateTimeOriginal')
        self.media_image.camera_manufacturer = service.get_exif_data_by_key('Make')
        self.media_image.camera_model = service.get_exif_data_by_key('Model')
        self.media_image.exif_image_height = service.get_exif_data_by_key('ExifImageHeight')
        self.media_image.exif_image_width = service.get_exif_data_by_key('ExifImageWidth')

        self.media_image.megapixels = self.get_image_megapixels()

        self.media_image.save()

        return self.media_image

    def get_media_image_sized_from_dimensions(self, height: int, width: int, approximate=False) -> StorageMediaImageSized:
        """
        Retrieve the StorageMediaImageSized object that corresponds to a given height and width. It may
        optionally approximate the selection (always selecting the highest quality dimension that is fulfilled by
        the given size).
        :param height:
        :param width:
        :param approximate:
        :return:
        """
        try:
            return StorageMediaImageSized.objects.get(media_image=self.media_image, height=height, width=width)
        except StorageMediaImageSized.DoesNotExist:
            if not approximate:
                raise
            dimensions_list = StorageMediaImageSized.objects.filter(
                media_image=self.media_image,
                height__lte=height,
                width__lte=width,
            ).order_by('-megapixels')
            if len(dimensions_list) == 0:
                raise
            return dimensions_list[0]

    def get_image_megapixels(self) -> float:
        return float(self.media_image.height * self.media_image.width) / 1000000
