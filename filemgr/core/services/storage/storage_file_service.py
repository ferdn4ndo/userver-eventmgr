from core.models import StorageFile, CustomUser
from core.services.storage.storage_service import StorageService
from core.services.storage_drivers.generic_storage_driver import GenericStorageDriver


class StorageFileService:
    storage_file: StorageFile

    def __init__(self, storage_file: StorageFile):
        self.storage_file = storage_file

    def load_driver(self) -> GenericStorageDriver:
        storage = self.storage_file.storage
        service = StorageService(storage=storage)

        return service.load_driver()

    def delete_file(self, user: CustomUser):
        self.storage_file.excluded = True
        self.storage_file.updated_by = user
        self.storage_file.save()
