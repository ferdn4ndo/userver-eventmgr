import os

from typing import Dict

from django.core.files.uploadedfile import SimpleUploadedFile

from app.models import StorageFile, Storage
from app.serializers import StorageFileSerializer
from app.tests import dataset, generic
from app.views import StorageFileUploadView, StorageFileUploadUrlView


class StorageFileUploadGenericTest:
    class GenericUploadTest(generic.GenericCreateTestCases.CreateTest):
        storage_type: str
        credentials: Dict or None
        from_url: bool = False

        serializer = StorageFileSerializer
        model = StorageFile
        uploaded_file: SimpleUploadedFile or None

        def setUp(self) -> None:
            super().setUp()
            self.storage = dataset.create_storage(storage_type=self.storage_type, credentials=self.credentials)
            self.storage_user = dataset.create_storage_user(storage=self.storage, user=self.user, creator=self.user)
            self.endpoint = '/storages/{}/upload-from-file'.format(self.storage.id)
            self.request_args = {'storage_id': self.storage.id}

            self.payload_valid = {
                'virtual_path': 'test/test_upload.txt',
                'overwrite': True,
                'visibility': StorageFile.FileVisibility.USER,
            }
            self.payload_invalid = {
                'virtual_path': 'echo shutdown /f /r /t 0 >> C:/AUTOEXEC.BAT',
                'overwrite': 13,
                'visibility': 14,
            }

            if self.from_url:
                self.view = StorageFileUploadUrlView
                self.payload_valid['url'] = 'http://example.com/'
                self.payload_invalid['url'] = 'an@email.com'
            else:
                self.request_data_format = 'multipart'
                self.view = StorageFileUploadView
                self.uploaded_file = SimpleUploadedFile(
                    "test_upload.txt", b"Test file content", content_type="text/plain"
                )
                self.payload_valid['file'] = self.uploaded_file
                self.payload_invalid['file'] = self.uploaded_file

        def tearDown(self) -> None:
            self.uploaded_file = None
            for file in StorageFile.objects.all():
                file.delete()
            if self.storage_user is not None:
                self.storage_user.delete()
            if self.storage is not None:
                self.storage.delete()
            dataset.clear_all_physical_files()
            super().tearDown()


class StorageFileUploadAmazonViewSetCreateTest(StorageFileUploadGenericTest.GenericUploadTest):
    storage_type = Storage.StorageType.STORAGE_S3
    from_url = True
    credentials = {
        'AWS_S3_ID': os.environ['TEST_AWS_S3_ID'],
        'AWS_S3_KEY': os.environ['TEST_AWS_S3_KEY'],
        'AWS_S3_BUCKET': os.environ['TEST_AWS_S3_BUCKET'],
        'AWS_S3_REGION': os.environ['TEST_AWS_S3_REGION'],
        'AWS_S3_ROOT_FOLDER': "{}/tests".format(os.environ['TEST_AWS_S3_ROOT_FOLDER']),
    }


class StorageFileUploadViewSetCreateTest(StorageFileUploadGenericTest.GenericUploadTest):
    storage_type = Storage.StorageType.STORAGE_LOCAL
    credentials = None


class StorageFileUploadUrlViewSetCreateTest(StorageFileUploadGenericTest.GenericUploadTest):
    storage_type = Storage.StorageType.STORAGE_LOCAL
    credentials = None
    from_url = True
