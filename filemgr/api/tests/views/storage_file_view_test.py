import uuid

from app.models import StorageFile
from app.serializers import StorageFileSerializer
from app.tests import dataset, generic
from app.views import StorageFileViewSet


class StorageFileViewSetDestroyTest(generic.GenericDestroyTestCase.DestroyTest):
    serializer = StorageFileSerializer
    model = StorageFile
    view = StorageFileViewSet
    model_fake_id = uuid.uuid4()

    def setUp(self) -> None:
        super(StorageFileViewSetDestroyTest, self).setUp()
        self.storage = dataset.create_storage()
        self.endpoint = '/storages/{}/files/'.format(self.storage.id)
        self.request_args = {'storage_id': self.storage.id}

        self.storage_user = dataset.create_storage_user(storage=self.storage, user=self.user, creator=self.user)
        self.storage_file = dataset.create_storage_file(storage=self.storage, user=self.user)
        self.model_real_id = self.storage_file.id

    def tearDown(self) -> None:
        if self.storage_file is not None:
            self.storage_file.delete()
        if self.storage_user is not None:
            self.storage_user.delete()
        if self.storage is not None:
            self.storage.delete()
        dataset.clear_all_physical_files()
        super(StorageFileViewSetDestroyTest, self).tearDown()


class StorageFileViewSetListTest(generic.GenericListTestCase.ListTest):
    serializer = StorageFileSerializer
    model = StorageFile
    view = StorageFileViewSet
    expected_items = 20

    def setUp(self) -> None:
        super(StorageFileViewSetListTest, self).setUp()
        self.storage = dataset.create_storage()
        self.endpoint = '/storages/{}/files/'.format(self.storage.id)
        self.request_args = {'storage_id': self.storage.id}

        self.storage_user = dataset.create_storage_user(storage=self.storage, user=self.user, creator=self.user)
        self.storage_files = dataset.create_storage_files(storage=self.storage, user=self.user, total_files=20)

    def tearDown(self) -> None:
        for file in self.storage_files:
            file.delete()
        if self.storage_user is not None:
            self.storage_user.delete()
        if self.storage is not None:
            self.storage.delete()
        dataset.clear_all_physical_files()
        super(StorageFileViewSetListTest, self).tearDown()


class StorageFileViewSetPartialUpdateTest(generic.GenericPartialUpdateTestCase.PartialUpdateTest):
    serializer = StorageFileSerializer
    model = StorageFile
    view = StorageFileViewSet
    model_fake_id = uuid.uuid4()

    def setUp(self) -> None:
        super(StorageFileViewSetPartialUpdateTest, self).setUp()
        self.storage = dataset.create_storage()
        self.endpoint = '/storages/{}/files/'.format(self.storage.id)
        self.request_args = {'storage_id': self.storage.id}

        self.payload_valid = {
            'visibility': StorageFile.FileVisibility.PUBLIC,
            'metadata': {
                'language': 'en-us'
            },
            'virtual_path': 'test/file1.txt'
        }
        self.payload_invalid = {
            'visibility': 'aaaaa',
            'metadata': 123,
            'virtual_path': 0,
        }

        self.storage_user = dataset.create_storage_user(storage=self.storage, user=self.user, creator=self.user)
        self.storage_file = dataset.create_storage_file(storage=self.storage, user=self.user)
        self.model_real_id = self.storage_file.id

    def tearDown(self) -> None:
        if self.storage_file is not None:
            self.storage_file.delete()
        if self.storage_user is not None:
            self.storage_user.delete()
        if self.storage is not None:
            self.storage.delete()
        dataset.clear_all_physical_files()
        super(StorageFileViewSetPartialUpdateTest, self).tearDown()


class StorageFileViewSetRetrieveTest(generic.GenericRetrieveTestCase.RetrieveTest):
    serializer = StorageFileSerializer
    model = StorageFile
    view = StorageFileViewSet
    model_fake_id = uuid.uuid4()

    def setUp(self) -> None:
        super(StorageFileViewSetRetrieveTest, self).setUp()
        self.storage = dataset.create_storage()
        self.endpoint = '/storages/{}/files/'.format(self.storage.id)
        self.request_args = {'storage_id': self.storage.id}

        self.storage_user = dataset.create_storage_user(storage=self.storage, user=self.user, creator=self.user)
        self.storage_file = dataset.create_storage_file(storage=self.storage, user=self.user)
        self.model_real_id = self.storage_file.id

    def tearDown(self) -> None:
        if self.storage_file is not None:
            self.storage_file.delete()
        if self.storage_user is not None:
            self.storage_user.delete()
        if self.storage is not None:
            self.storage.delete()
        dataset.clear_all_physical_files()
        super(StorageFileViewSetRetrieveTest, self).tearDown()
