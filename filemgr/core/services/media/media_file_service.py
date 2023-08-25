import os

from django.forms import model_to_dict
from django_q.tasks import async_task

from core.models import StorageFile, StorageFileMimeType
from core.services.logger.logger_service import get_logger
from core.services.message_broker.message_broker_service import MessageBrokerService


class MediaFileService:

    def __init__(self, storage_file: StorageFile):
        self.logger = get_logger(__name__)
        self.storage_file = storage_file

    def is_media_file(self) -> bool:
        generic_media_types = [
            StorageFileMimeType.GenericTypes.IMAGE,
            StorageFileMimeType.GenericTypes.VIDEO,
        ]

        return self.storage_file.type.generic_type in generic_media_types

    def _publish_file(self):
        # Put the file in the queue
        MessageBrokerService().send_message(
            topic='storage_file_published',
            payload=model_to_dict(self.storage_file)
        )

    def _process_image_file(self):
        async_task('core.services.media.media_image_worker.process_media_image', self.storage_file)

    def _process_video_file(self):
        pass

    def process_media_file(self, force: bool = False):
        if not force and self.storage_file.status != StorageFile.FileStatus.UPLOADED:
            self.logger.warning(
                f"Media processing skipped file {self.storage_file.id}"
                f" as its status is '{self.storage_file.status}'"
                f" (expecting '{StorageFile.FileStatus.UPLOADED}'"
            )

        if self.storage_file.type.generic_type == StorageFileMimeType.GenericTypes.IMAGE:
            self._process_image_file()

        if self.storage_file.type.generic_type == StorageFileMimeType.GenericTypes.VIDEO:
            self._process_video_file()

        self._publish_file()

        return self.storage_file

    def process_if_is_media_file(self, force: bool = False):
        if self.is_media_file():
            self.process_media_file(force=force)
        else:
            self.logger.info(f"File id {self.storage_file.id} processing skipped as it's not media!")
