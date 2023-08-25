import uuid

from app.models import Storage
from app.serializers import StorageSerializer
from app.tests import dataset, generic
from app.views import StorageViewSet


class StorageViewSetCreateTest(generic.GenericCreateTestCases.CreateTest):
    endpoint = '/storages/'
    serializer = StorageSerializer
    model = Storage
    requires_admin = True
    view = StorageViewSet
    payload_valid = {
        'type': Storage.StorageType.STORAGE_LOCAL,
        'credentials': {
            'user': 'foo',
            'pass': 'bar',
        }
    }
    payload_invalid = {
        'type': 'foooo',
        'credentials': {
            'user': 'foo',
            'pass': 'bar',
        }
    }


class StorageViewSetDestroyTest(generic.GenericDestroyTestCase.DestroyTest):
    endpoint = '/storages/'
    serializer = StorageSerializer
    model = Storage
    requires_admin = True
    view = StorageViewSet
    model_fake_id = uuid.uuid4()

    def setUp(self) -> None:
        super(StorageViewSetDestroyTest, self).setUp()
        self.storage = dataset.create_storage()
        self.model_real_id = self.storage.id

    def tearDown(self) -> None:
        if self.storage is not None:
            self.storage.delete()
        super(StorageViewSetDestroyTest, self).tearDown()


class StorageViewSetListTest(generic.GenericListTestCase.ListTest):
    endpoint = '/storages/'
    serializer = StorageSerializer
    model = Storage
    requires_admin = True
    view = StorageViewSet
    expected_items = 20

    def setUp(self) -> None:
        super(StorageViewSetListTest, self).setUp()
        self.storages = dataset.create_storages(total=self.expected_items)

    def tearDown(self) -> None:
        for storage in self.storages:
            storage.delete()
        super(StorageViewSetListTest, self).tearDown()


class StorageViewSetPartialUpdateTest(generic.GenericPartialUpdateTestCase.PartialUpdateTest):
    endpoint = '/storages/'
    serializer = StorageSerializer
    model = Storage
    requires_admin = True
    view = StorageViewSet
    model_fake_id = uuid.uuid4()
    payload_valid = {
        'type': Storage.StorageType.STORAGE_LOCAL,
        'credentials': {
            'user': 'foo',
            'pass': 'bar',
        }
    }
    payload_invalid = {
        'type': 'foooo',
        'credentials': 1234
    }

    def setUp(self) -> None:
        super(StorageViewSetPartialUpdateTest, self).setUp()
        self.storage = dataset.create_storage()
        self.model_real_id = self.storage.id

    def tearDown(self) -> None:
        if self.storage is not None:
            self.storage.delete()
        super(StorageViewSetPartialUpdateTest, self).tearDown()


class StorageViewSetRetrieveTest(generic.GenericRetrieveTestCase.RetrieveTest):
    endpoint = '/storages/'
    serializer = StorageSerializer
    model = Storage
    requires_admin = True
    view = StorageViewSet
    model_fake_id = uuid.uuid4()

    def setUp(self) -> None:
        super(StorageViewSetRetrieveTest, self).setUp()
        self.storage = dataset.create_storage()
        self.model_real_id = self.storage.id

    def tearDown(self) -> None:
        if self.storage is not None:
            self.storage.delete()
        super(StorageViewSetRetrieveTest, self).tearDown()
