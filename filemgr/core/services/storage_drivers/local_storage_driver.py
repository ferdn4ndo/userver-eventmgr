import os
from pathlib import Path
import shutil
from shutil import copyfile

from core.services.storage_drivers.generic_storage_driver import GenericStorageDriver
from core.models.storage.storage_file_model import StorageFile
from core.services.web_request.web_request_service import WebRequestService


class LocalStorageDriver(GenericStorageDriver):
    """
    Storage driver class for local files
    """

    def get_remote_root_path(self) -> str:
        """
        Returns the remote root path. Should be implemented for each storage.
        :return: The root path
        """
        return os.environ['LOCAL_TEST_STORAGE_ROOT']

    def _prepare_parent_folder(self, remote_path: str) -> None:
        """
        Creates the parent folder of a remote path (if not created) and fix its
        ownership.
        :param remote_path: the remote path to create the parent folders
        """
        parent_folder = Path(remote_path).parent
        Path(parent_folder).mkdir(parents=True, exist_ok=True)
        os.chown(parent_folder, 1000, 1000)

    def perform_upload_from_path(self, local_path: str, remote_path: str):
        """
        Upload a file from a local path
        :param local_path: the local path of the file that's going to be uploaded
        :param remote_path: the remote path to where the file should be uploaded
        """
        self._prepare_parent_folder(remote_path=remote_path)

        copyfile(local_path, remote_path)
        os.chown(remote_path, 1000, 1000)

    def perform_upload_from_url(self, url: str, remote_path: str):
        """
        Upload a file from a given url
        :param url: the url of the file that's going to be uploaded
        :param remote_path: the remote path to where the file should be uploaded
        """
        req_for_file = WebRequestService(url=url, stream=True)
        with req_for_file.object as request_file:
            request_file.raise_for_status()

            self._prepare_parent_folder(remote_path=remote_path)

            with open(remote_path, 'wb') as physical_file:
                shutil.copyfileobj(request_file.raw, physical_file)
            os.chown(remote_path, 1000, 1000)

    def perform_download_to_path(self, remote_path: str, local_dest: str):
        """
        Download a file from the remote storage
        :param remote_path: the real remote path from where the file will be downloaded
        :param local_dest: the destination file path of the download
        :return:
        """
        copyfile(remote_path, local_dest)

    def generate_download_url(self, file: StorageFile, expiration_seconds: int = 3600, force_download: bool = False) -> str:
        """
        Retrieve an expirable download url for a given storage file
        :param file: the StorageFile model to be downloaded
        :param force_download: if the file download should be enforced (not rendered)
        :param expiration_seconds: time in seconds for the URL to remain valid. 0 for the infinite and beyond.
        :return:
        """
        return self.get_real_remote_path(file)

    def perform_delete(self, file: StorageFile):
        """
        Performs the remote file deletion given a StorageFile. Implement this method with the storage logic.
        :param file: the StorageFile model to be deleted
        :return:
        """
        os.remove(self.get_real_remote_path(file))

    def remote_file_exists(self, file: StorageFile) -> bool:
        """
        Determines if a given real remote path exists
        :param file: the file to check whether its remote path exists
        :return: boolean indicating if the file exists or not
        """
        return os.path.isfile(self.get_real_remote_path(file))
