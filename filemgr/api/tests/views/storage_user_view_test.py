import uuid

from app.models import StorageUser
from app.serializers import StorageUserSerializer
from app.tests import dataset, generic
from app.views import StorageUserViewSet


class StorageUserViewSetCreateTest(generic.GenericCreateTestCases.CreateTest):
    serializer = StorageUserSerializer
    model = StorageUser
    requires_admin = True
    view = StorageUserViewSet

    def setUp(self) -> None:
        super().setUp()
        self.storage = dataset.create_storage()
        self.user1 = dataset.create_user()
        self.payload_valid = {
            'user': self.user1.username,
            'may_write': True,
            'may_read': True,
        }
        self.payload_invalid = {
            'user': self.user1.username,
            'may_write': 1234,
            'may_read': 4553,
        }
        self.endpoint = '/storages/{}/users/'.format(self.storage.id)
        self.request_args = {'storage_id': self.storage.id}

    def tearDown(self) -> None:
        if self.user1 is not None:
            self.user1.delete()
        if self.storage is not None:
            self.storage.delete()
        super().tearDown()


class StorageUserViewSetDestroyTest(generic.GenericDestroyTestCase.DestroyTest):
    serializer = StorageUserSerializer
    model = StorageUser
    requires_admin = True
    view = StorageUserViewSet
    model_fake_id = uuid.uuid4()

    def setUp(self) -> None:
        super().setUp()
        self.storage = dataset.create_storage()
        self.user1 = dataset.create_user()
        self.endpoint = '/storages/{}/users/'.format(self.storage.id)
        self.request_args = {'storage_id': self.storage.id}
        self.storage_user = dataset.create_storage_user(storage=self.storage, user=self.user1, creator=self.user)
        self.model_real_id = self.storage_user.id

    def tearDown(self) -> None:
        if self.storage_user is not None:
            self.storage_user.delete()
        if self.user1 is not None:
            self.user1.delete()
        if self.storage is not None:
            self.storage.delete()
        super().tearDown()


class StorageUserViewSetListTest(generic.GenericListTestCase.ListTest):
    serializer = StorageUserSerializer
    model = StorageUser
    requires_admin = True
    view = StorageUserViewSet
    expected_items = 20

    def setUp(self) -> None:
        super().setUp()
        self.storage = dataset.create_storage()
        self.storage_users = dataset.create_storage_users(storage=self.storage, total_users=20, creator=self.user)
        self.endpoint = '/storages/{}/users/'.format(self.storage.id)
        self.request_args = {'storage_id': self.storage.id}

    def tearDown(self) -> None:
        for user in self.storage_users:
            user.delete()
        if self.storage is not None:
            self.storage.delete()
        super().tearDown()


class StorageUserViewSetPartialUpdateTest(generic.GenericPartialUpdateTestCase.PartialUpdateTest):
    serializer = StorageUserSerializer
    model = StorageUser
    requires_admin = True
    view = StorageUserViewSet
    model_fake_id = uuid.uuid4()

    def setUp(self) -> None:
        super().setUp()
        self.storage = dataset.create_storage()
        self.user1 = dataset.create_user()
        self.payload_valid = {
            'user': self.user1.username,
            'may_write': True,
            'may_read': True,
        }
        self.payload_invalid = {
            'user': self.user1.username,
            'may_write': 1234,
            'may_read': 4553,
        }
        self.endpoint = '/storages/{}/users/'.format(self.storage.id)
        self.request_args = {'storage_id': self.storage.id}
        self.storage_user = dataset.create_storage_user(storage=self.storage, user=self.user1, creator=self.user)
        self.model_real_id = self.storage_user.id

    def tearDown(self) -> None:
        if self.user1 is not None:
            self.user1.delete()
        if self.storage is not None:
            self.storage.delete()
        super().tearDown()


class StorageUserViewSetRetrieveTest(generic.GenericRetrieveTestCase.RetrieveTest):
    serializer = StorageUserSerializer
    model = StorageUser
    requires_admin = True
    view = StorageUserViewSet
    model_fake_id = uuid.uuid4()

    def setUp(self) -> None:
        super().setUp()
        self.storage = dataset.create_storage()
        self.user1 = dataset.create_user()
        self.endpoint = '/storages/{}/users/'.format(self.storage.id)
        self.request_args = {'storage_id': self.storage.id}
        self.storage_user = dataset.create_storage_user(storage=self.storage, user=self.user1, creator=self.user)
        self.model_real_id = self.storage_user.id

    def tearDown(self) -> None:
        if self.user1 is not None:
            self.user1.delete()
        if self.storage is not None:
            self.storage.delete()
        super().tearDown()
