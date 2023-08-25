import uuid

from app.models import StorageFileDownload
from app.serializers import StorageFileDownloadSerializer
from app.tests import dataset, generic
from app.views import StorageFileDownloadViewSet


class StorageFileDownloadViewSetCreateTest(generic.GenericCreateTestCases.CreateTest):
    serializer = StorageFileDownloadSerializer
    model = StorageFileDownload
    view = StorageFileDownloadViewSet

    def setUp(self) -> None:
        super().setUp()
        self.storage = dataset.create_storage()
        self.storage_user = dataset.create_storage_user(storage=self.storage, user=self.user, creator=self.user)
        self.storage_file = dataset.create_storage_file(storage=self.storage, user=self.user)
        self.endpoint = '/storages/{}/files/{}/download'.format(self.storage.id, self.storage_file.id)
        self.request_args = {'storage_id': self.storage.id, 'file_id': self.storage_file.id}
        self.payload_valid = {}

    def tearDown(self) -> None:
        for download in StorageFileDownload.objects.all():
            download.delete()
        if self.storage_file is not None:
            self.storage_file.delete()
        if self.storage_user is not None:
            self.storage_user.delete()
        if self.storage is not None:
            self.storage.delete()
        super().tearDown()


class StorageFileDownloadViewSetListTest(generic.GenericListTestCase.ListTest):
    serializer = StorageFileDownloadSerializer
    model = StorageFileDownload
    view = StorageFileDownloadViewSet
    expected_items = 20

    def setUp(self) -> None:
        super().setUp()
        self.storage = dataset.create_storage()
        self.storage_user = dataset.create_storage_user(storage=self.storage, user=self.user, creator=self.user)
        self.storage_file = dataset.create_storage_file(storage=self.storage, user=self.user)
        self.endpoint = '/storages/{}/files/{}/download'.format(self.storage.id, self.storage_file.id)
        self.request_args = {'storage_id': self.storage.id, 'file_id': self.storage_file.id}
        self.storage_file_downloads = dataset.create_storage_file_downloads(
            file=self.storage_file,
            user=self.user,
            total_downloads=20
        )

    def tearDown(self) -> None:
        for download in self.storage_file_downloads:
            download.delete()
        if self.storage_file is not None:
            self.storage_file.delete()
        if self.storage_user is not None:
            self.storage_user.delete()
        if self.storage is not None:
            self.storage.delete()
        super().tearDown()


class StorageFileDownloadViewSetRetrieveTest(generic.GenericRetrieveTestCase.RetrieveTest):
    serializer = StorageFileDownloadSerializer
    model = StorageFileDownload
    view = StorageFileDownloadViewSet
    model_fake_id = uuid.uuid4()

    def setUp(self) -> None:
        super().setUp()
        self.storage = dataset.create_storage()
        self.storage_user = dataset.create_storage_user(storage=self.storage, user=self.user, creator=self.user)
        self.storage_file = dataset.create_storage_file(storage=self.storage, user=self.user)
        self.endpoint = '/storages/{}/files/{}/download'.format(self.storage.id, self.storage_file.id)
        self.request_args = {'storage_id': self.storage.id, 'file_id': self.storage_file.id}

        self.download = dataset.create_storage_file_download(file=self.storage_file, user=self.user)
        self.model_real_id = self.download.id

    def tearDown(self) -> None:
        if self.download is not None:
            self.download.delete()
        if self.storage_file is not None:
            self.storage_file.delete()
        if self.storage_user is not None:
            self.storage_user.delete()
        if self.storage is not None:
            self.storage.delete()
        dataset.clear_all_physical_files()
        super().tearDown()
