import os
import random
import string
import tempfile
from typing import Dict, List

from app.drivers import load_storage_driver
from app.models import Storage, StorageFile, CustomUser, StorageUser, StorageFileDownload

from core.services.storage.storage_service import StorageService


def create_request_url(endpoint: str = ''):
    protocol = 'https' if 'LETSENCRYPT_HOST' in os.environ else 'http'

    url = "{}://{}/{}".format(protocol, os.environ['VIRTUAL_HOST'], endpoint)
    return url


def create_storage(storage_type: str = Storage.StorageType.STORAGE_LOCAL, credentials: Dict = None) -> Storage:
    if credentials is None:
        credentials = {'foo': 'bar'}

    storage = Storage(
        type=storage_type,
        credentials=credentials
    )
    storage.save()
    return storage


def create_storages(total: int = 1) -> List:
    return [create_storage() for x in range(0, total)]


def get_random_string(length: int = 10) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def create_user(username: str = None, is_admin=False) -> CustomUser:
    if username is None:
        username = get_random_string()
    user = CustomUser(
        username=username,
        system_name=os.environ['USERVER_AUTH_SYSTEM_NAME'],
        is_admin=is_admin,
        is_active=True,
    )
    user.save()
    return user


def create_storage_file(storage: Storage, user: CustomUser) -> StorageFile:
    driver = StorageService(storage=storage).load_driver()
    temp_filepath = os.path.join(tempfile.gettempdir(), "{}.txt".format(get_random_string()))
    with open(temp_filepath, 'wb+') as f:
        f.write(b'Test file')

    storage_file = driver.upload_from_path(
        user=user,
        path=temp_filepath,
        overwrite=True,
        visibility=StorageFile.FileVisibility.PUBLIC,
    )
    return storage_file


def create_storage_files(storage: Storage, user: CustomUser, total_files: int = 10):
    return [create_storage_file(storage=storage, user=user) for x in range(0, total_files)]


def clear_all_physical_files():
    """ Use it with EXTREME caution"""
    dirs = [os.environ['LOCAL_TEST_STORAGE_ROOT'], tempfile.gettempdir()]
    for folder in dirs:
        for filename in os.listdir(folder):
            if filename == '.gitkeep':
                continue

            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


def create_storage_user(
        storage: Storage,
        user: CustomUser,
        may_read: bool = True,
        may_write: bool = True,
        creator: CustomUser = None
) -> StorageUser:
    storage_user = StorageUser(
        storage=storage,
        user=user,
        may_read=may_read,
        may_write=may_write,
        created_by=creator,
    )
    storage_user.save()
    return storage_user


def create_storage_users(
        storage: Storage,
        may_read: bool = True,
        may_write: bool = True,
        total_users: int = 10,
        creator: CustomUser = None
):
    users = [create_user() for x in range(0, total_users)]
    storage_users = [
        create_storage_user(storage=storage, user=user, may_read=may_read, may_write=may_write, creator=creator)
        for user in users
    ]
    return storage_users


def create_storage_file_download(file: StorageFile, user: CustomUser):
    download = StorageFileDownload(
        storage_file=file,
        owner=user
    )
    download.save()
    return download


def create_storage_file_downloads(file: StorageFile, user: CustomUser, total_downloads: int = 10):
    downloads = [create_storage_file_download(file=file, user=user) for x in range(0, total_downloads)]
    return downloads
