from core.exceptions.storage_driver_exception import StorageDriverException
from core.models.storage.storage_model import Storage
from core.models.storage.storage_file_model import StorageFile
from core.services.storage_drivers.amazon_s3_storage_driver import AmazonS3StorageDriver
from core.services.storage_drivers.generic_storage_driver import GenericStorageDriver
from core.services.storage_drivers.local_storage_driver import LocalStorageDriver


class StorageService:
    storage: Storage

    def __init__(self, storage: Storage):
        self.storage = storage

    @staticmethod
    def delete_storage(storage: Storage):
        storage_files = StorageFile.objects.filter(storage=storage)
        for storage_file in storage_files:
            storage_file.comment.delete()
            storage_file.delete()

        storage.delete()


    def load_driver(self) -> GenericStorageDriver:
        if self.storage.type == Storage.StorageType.STORAGE_S3:
            return AmazonS3StorageDriver(storage=self.storage)
        elif self.storage.type == Storage.StorageType.STORAGE_LOCAL:
            return LocalStorageDriver(storage=self.storage)

        raise StorageDriverException(f"Unknown storage type '{self.storage.type}' for ID '{self.storage.id}'")
