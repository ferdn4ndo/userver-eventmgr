import os
from abc import ABC, abstractmethod
from pathlib import Path
import pathlib
from typing import Union
from urllib.parse import urlparse

import magic
from django.core.cache import cache
from django.core.files.uploadedfile import TemporaryUploadedFile, InMemoryUploadedFile
from django.forms import model_to_dict
from django.utils.translation import gettext_lazy as _

from core.exceptions.invalid_argument_class_exception import InvalidArgumentClassException
from core.exceptions.storage_driver_exception import StorageDriverException
from core.models.storage.storage_file_mime_type_model import StorageFileMimeType
from core.models.storage.storage_file_model import StorageFile
from core.models.storage.storage_model import Storage
from core.models.user.user_model import CustomUser
from core.services.file.file_service import FileService
from core.services.media.media_file_service import MediaFileService
from core.services.message_broker.message_broker_service import MessageBrokerService
from core.services.photo.photo_exif_service import PhotoExifService
from core.services.translation.translation_service import Messages
from core.services.web_request.web_request_service import WebRequestService


class GenericStorageDriver(ABC):
    """
    Abstract class representing a generic storage driver
    """

    def __init__(self, storage: Storage):
        """
        Class constructor
        """
        self.storage = storage

    @abstractmethod
    def get_remote_root_path(self) -> str:
        """
        Returns the remote root path. Should be implemented for each storage.
        :return: The root path
        """
        raise NotImplementedError(Messages.MSG_TO_BE_IMPLEMENTED)

    @abstractmethod
    def perform_upload_from_path(self, local_path: str, remote_path: str):
        """
        Upload a file from a local path
        :param local_path: the local path of the file that's going to be uploaded
        :param remote_path: the real remote path to write the file
        """
        raise NotImplementedError(Messages.MSG_TO_BE_IMPLEMENTED)

    @abstractmethod
    def perform_upload_from_url(self, url: str, remote_path: str):
        """
        Upload a file from a given url
        :param url: the url of the file that's going to be uploaded
        :param remote_path: the real remote path to write the file
        :return:
        """
        raise NotImplementedError(Messages.MSG_TO_BE_IMPLEMENTED)

    @abstractmethod
    def perform_download_to_path(self, remote_path: str, local_dest: str):
        """
        Download a file from the remote storage
        :param remote_path: the real remote path from where the file will be downloaded
        :param local_dest: the destination file path of the download
        :return:
        """
        raise NotImplementedError(Messages.MSG_TO_BE_IMPLEMENTED)

    def get_download_url(self, file: StorageFile, expiration_seconds: int = 3600, force_download: bool = False):
        """
        Retrieve an expirable download url for a given storage file (value is cached while not expired)
        :param file: the StorageFile model to be downloaded
        :param force_download: if the file download should be enforced (not rendered)
        :param expiration_seconds: time in seconds for the URL to remain valid. 0 for the infinite and beyond.
        :return:
        """
        key = f'download_url_{"DOWNLOAD" if force_download else "INLINE"}_{file.id}'
        cached_value = cache.get(key)
        if cached_value is not None:
            return cached_value

        url = self.generate_download_url(
            file=file,
            expiration_seconds=expiration_seconds,
            force_download=force_download,
        )
        cache.set(key, url, expiration_seconds)

        return url

    @abstractmethod
    def generate_download_url(self, file: StorageFile, expiration_seconds: int = 3600, force_download: bool = False) -> str:
        """
        Retrieve an expirable download url for a given storage file
        :param file: the StorageFile model to be downloaded
        :param force_download: if the file download should be enforced (not rendered)
        :param expiration_seconds: time in seconds for the URL to remain valid. 0 for the infinite and beyond.
        :return:
        """
        raise NotImplementedError(Messages.MSG_TO_BE_IMPLEMENTED)

    @abstractmethod
    def perform_delete(self, file: StorageFile):
        """
        Performs the remote file deletion given a StorageFile. Implement this method with the storage logic.
        :param file: the StorageFile model to be deleted
        :return:
        """
        raise NotImplementedError(Messages.MSG_TO_BE_IMPLEMENTED)

    @abstractmethod
    def remote_file_exists(self, file: StorageFile) -> bool:
        """
        Determines if a given real remote path exists
        :param file: the file to check whether its remote path exists
        :return: boolean indicating if the file exists or not
        """
        raise NotImplementedError(Messages.MSG_TO_BE_IMPLEMENTED)

    def get_real_remote_path(self, file: StorageFile, subfolder: str = None) -> str:
        """
        Get the real remote path for a StoreFile (usually different from the 'visual' remote_path)
        :param file: the file to retrieve the path
        :param subfolder: the sub-folder to retrieve the path
        :return: the file path
        """
        path_parts = []

        remote_root_path = self.get_remote_root_path()
        if remote_root_path:
            path_parts.append(remote_root_path)

        if subfolder:
            path_parts.append(subfolder)

        path_parts.append(f"{str(file.id)}{file.extension}")

        return os.path.join(*path_parts)

    def _inform_file_uploaded(self, storage_file: StorageFile):
        MessageBrokerService().send_message(
            topic=f'storages.{self.storage.id}.file_uploaded',
            payload=model_to_dict(storage_file)
        )

    def upload_from_path(
            self,
            user: CustomUser,
            path: str,
            name: str = "",
            virtual_path: str = "",
            original_path: str = "",
            origin: str = StorageFile.FileOrigin.UNKNOWN,
            overwrite: bool = False,
            visibility: str = StorageFile.FileVisibility.USER,
            is_url: bool = False,
    ) -> StorageFile:
        """
        Upload a file from a local path or a URL. Please do not modify this method. Instead, put the storage-specific
        upload instructions in the "perform_upload_from_path" or "perform_upload_from_url" method, respectively.
        :param user: the user performing the upload (owner of the file)
        :param name: the file name that's going to be uploaded
        :param path: the file path (local or url) that's going to be uploaded
        :param original_path: the path of the file in the origin system before being uploaded
        :param origin: the origin of the file
        :param virtual_path: the virtual remote path to where the file should be uploaded
        :param overwrite: if the file should be replaced in case the remote path already exists
        :param visibility: file visibility (one of StorageFile.FileVisibility options)
        :param is_url: if the "path" argument is a URL (True) or a local file path (False)
        :return:
        """
        storage_file = self.perform_basic_upload_operations(
            user=user,
            path=path,
            name=name,
            virtual_path=virtual_path,
            original_path=original_path,
            origin=origin,
            overwrite=overwrite,
            visibility=visibility,
            is_url=is_url,
        )

        # Process media file
        service = MediaFileService(storage_file=storage_file)
        storage_file = service.process_media_file()

        return storage_file

    def perform_basic_upload_operations(
            self,
            user: CustomUser,
            path: str,
            name: str = "",
            virtual_path: str = "",
            original_path: str = "",
            origin: str = StorageFile.FileOrigin.UNKNOWN,
            overwrite: bool = False,
            visibility: str = StorageFile.FileVisibility.USER,
            is_url: bool = False,
            size_tag: str = "",
    ) -> StorageFile:
        storage_file = self.create_empty_file_resource(user)
        storage_file.origin = origin
        storage_file.status = StorageFile.FileStatus.UPLOADING
        storage_file.name = name
        storage_file.visibility = visibility
        storage_file.original_path = original_path
        storage_file.owner = user
        storage_file.virtual_path = self.generate_virtual_path(storage_file, virtual_path=virtual_path, is_url=is_url)
        storage_file.real_path = self.get_real_remote_path(storage_file)

        # Check if the virtual_path (where the file should be uploaded) doesn't already exist
        self.check_if_virtual_path_exists(storage_file.virtual_path, raise_ex_if_yes=not overwrite)

        # ToDo: Delete file if exists

        # Call the appropriate file metadata reader to update the model
        if is_url:
            self.update_file_info_from_url(file=storage_file, file_url=path)
        else:
            self.update_file_info_from_local(file=storage_file, local_path=path)

        # Perform the upload by calling the appropriate method
        file_real_path = self.get_real_remote_path(
            file=storage_file,
            subfolder=None if not size_tag else f"resized/{size_tag}"
        )
        if is_url:
            self.perform_upload_from_url(url=path, remote_path=file_real_path)
        else:
            self.perform_upload_from_path(local_path=path, remote_path=file_real_path)
        storage_file.real_path = file_real_path
        storage_file.save()

        # Check if the file was really uploaded
        self.check_if_virtual_path_exists(storage_file.virtual_path, raise_ex_if_no=True)

        storage_file.status = StorageFile.FileStatus.UPLOADED
        storage_file.save()

        return storage_file

    def upload_from_request_file(
            self,
            user: CustomUser,
            request_file: Union[TemporaryUploadedFile, InMemoryUploadedFile],
            name: str = "",
            virtual_path: str = "",
            overwrite: bool = False,
            visibility: str = StorageFile.FileVisibility.USER,
            is_url: bool = False,
    ) -> StorageFile:
        """
        Upload a file from an upload request file object. In case it's in memory (for small files), persists the file
        on disk for further uploading through a normal file
        :param user: the user performing the upload (owner of the file)
        :param request_file: the request file object returned from the upload request
        :param name: the file name that's going to be uploaded
        :param virtual_path: the virtual remote path to where the file should be uploaded
        :param overwrite: if the file should be replaced in case the remote path already exists
        :param visibility: file visibility (one of StorageFile.FileVisibility options)
        :param is_url: if the "path" argument is a URL (True) or a local file path (False)
        :return:
        """
        if isinstance(request_file, TemporaryUploadedFile):
            temp_file_path = request_file.temporary_file_path()
        elif isinstance(request_file, InMemoryUploadedFile):
            temp_file_path = FileService().save_from_memory(memory_file=request_file)
        else:
            raise InvalidArgumentClassException(
                _("The request_file should be either a TemporaryUploadedFile or a InMemoryUploadedFile")
            )
        storage_file = self.upload_from_path(
            user=user,
            name=name,
            path=temp_file_path,
            original_path=request_file.name,
            origin=StorageFile.FileOrigin.LOCAL,
            virtual_path=virtual_path,
            overwrite=overwrite,
            visibility=visibility,
            is_url=is_url
        )

        storage_file.save()

        return storage_file

    def download_to_path(self, file: StorageFile, local_path: str, replace: bool = False):
        """
        Performs the download of a StorageFile to a local path
        Upload a file from a given url (should be implemented)
        :param file: the file (StorageFile model) to be downloaded
        :param local_path: the destination file path of the download
        :param replace: if the file should be replaced in case the local path already exists
        :return:
        """
        # Check if the local_path (where the file should be downloaded) doesn't already exist
        self.check_if_local_file_exists(local_path, raise_ex_if_yes=not replace)

        self.perform_download_to_path(self.get_real_remote_path(file), local_path)

        # Check if the file was really downloaded
        self.check_if_local_file_exists(local_path, raise_ex_if_no=True)

    def delete_file(self, file: StorageFile) -> bool:
        """
        Remotely deletes a StorageFile. Please do not modify this method. Instead, put the
        storage-specific delete instructions in the "perform_delete" method.
        :param file: the StorageFile model to be deleted
        :return:
        """
        if not self.remote_file_exists(file):
            return False

        self.perform_delete(file)
        file_exists = self.remote_file_exists(file)
        if file_exists:
            raise StorageDriverException("File wasn't deleted remotely")

        file.status = StorageFile.FileStatus.DELETED
        file.available = False
        file.excluded = True
        file.save()

        return True

    def virtual_path_exists(self, virtual_path) -> bool:
        """
        Determines if a given virtual path exists
        :param virtual_path:
        :return: boolean indicating if the file exists or not
        """
        file_count = StorageFile.objects.filter(
            storage=self.storage,
            virtual_path=virtual_path,
            excluded=False,
            available=True
        ).count()
        return True if file_count > 0 else False

    def check_if_virtual_path_exists(
            self,
            virtual_path: str,
            raise_ex_if_no: bool = False,
            raise_ex_if_yes: bool = False,
    ) -> bool:
        """
        Checks if a given virtual_path exists remotely, returning a boolean accordingly.
        However, if raise_ex_if_no is True and the file doesn't exist, a FileNotFoundError will be raised.
        Similarly, if raise_ex_if_yes is True and the file does exist, a FileExistsError will be raised.

        If the file doesn't exist and exist at the same time (are we quantum already?), the FileNotFoundError will
        be raised first.

        :param virtual_path: the path do be checked
        :param raise_ex_if_no: will raise a FileNotFoundError if the virtual_path doesn't exist
        :param raise_ex_if_yes: will raise a FileExistsError if the virtual_path does exist
        :return:
        """
        virtual_path_exists_bool = self.virtual_path_exists(virtual_path)

        if not virtual_path_exists_bool and raise_ex_if_no:
            raise FileNotFoundError(
                _("The file path '{}' should remotely exists and wasn't found.").format(virtual_path)
            )
        if virtual_path_exists_bool and raise_ex_if_yes:
            raise FileExistsError(
                _("The file path '{}' should not remotely exists but it does.").format(virtual_path)
            )
        return virtual_path_exists_bool

    @staticmethod
    def check_if_local_file_exists(
            local_path: str,
            raise_ex_if_no: bool = False,
            raise_ex_if_yes: bool = False,
    ) -> bool:
        """
        Checks if a given local_path exists locally, returning a boolean accordingly.
        However, if raise_ex_if_no is True and the file doesn't exist, a FileNotFoundError will be raised.
        Similarly, if raise_ex_if_yes is True and the file does exist, a FileExistsError will be raised.

        If the file doesn't exist and exist at the same time (are we quantum already?), the FileNotFoundError will
        be raised first.

        :param local_path: the path do be checked
        :param raise_ex_if_no: will raise a FileNotFoundError if the virtual_path doesn't exist
        :param raise_ex_if_yes: will raise a FileExistsError if the virtual_path does exist
        :return:
        """
        local_path_exists_bool = os.path.isfile(local_path)

        if not local_path_exists_bool and raise_ex_if_no:
            raise FileNotFoundError(
                _("The file path '{}' should locally exists and wasn't found.").format(local_path)
            )
        if local_path_exists_bool and raise_ex_if_yes:
            raise FileExistsError(
                _("The file path '{}' should locally exists and wasn't found.").format(local_path)
            )
        return local_path_exists_bool

    def create_empty_file_resource(self, user: CustomUser) -> StorageFile:
        """
        Create an empty file resource (database only)
        :param user:
        :return:
        """
        storage_file = StorageFile(
            storage=self.storage,
            created_by=user,
            updated_by=user,
        )
        storage_file.save()

        if self.remote_file_exists(storage_file):
            raise FileExistsError(_("Remote real file '{}' already exists (and should not)!").format(
                self.get_real_remote_path(storage_file)
            ))

        return storage_file

    @staticmethod
    def generate_virtual_path(file: StorageFile, virtual_path: str = None, is_url: bool = False) -> str:
        """
        Generate a remote virtual path for a given file
        :param file: The file resource being populated
        :param virtual_path: The filepath/url to base the filename (if auto)
        :param is_url: if it's an url (true) or a filepath (false)
        :return:
        """
        if virtual_path is None or virtual_path == "":
            return f"{file.id}{file.extension}"

        if is_url:
            url_parser = urlparse(virtual_path)
            return os.path.basename(url_parser.path)

        return virtual_path

    @staticmethod
    def update_file_info_from_local(file: StorageFile, local_path: str):
        """
        Update a StorageFile resource metadata based on a local file path
        :param file: The StorageFile resource going to be updated
        :param local_path: The file path to read information from
        """
        file.size = int(Path(local_path).stat().st_size)
        mime = magic.Magic(mime=True)
        guessed_mime = mime.from_file(local_path)

        if guessed_mime is not None:
            file.type = StorageFileMimeType.from_mime_type(guessed_mime)

        if file.type and file.type.generic_type == StorageFileMimeType.GenericTypes.IMAGE:
            service = PhotoExifService(file_path=local_path)
            file.exif_metadata = service.exif_data

        file.name = file.name if file.name != "" else FileService.get_name_from_path(file.original_path)
        file.extension = pathlib.Path(file.original_path).suffix
        file.hash = FileService(filepath=local_path).get_file_hash()
        file.save()

    @staticmethod
    def update_file_info_from_url(file: StorageFile, file_url: str):
        """
        Update a StorageFile resource metadata based on a local file path
        :param file: The StorageFile resource going to be updated
        :param file_url: The file url to read information from
        """
        url_info = WebRequestService.get_url_info(url=file_url)
        url_address_parser = urlparse(file_url)

        if 'Content-Length' in url_info:
            file.size = int(url_info['Content-Length'])

        file.type = StorageFileMimeType.from_mime_type(url_info['Content-Type'])
        file.origin = StorageFile.FileOrigin.WEB
        file.original_path = file_url
        file.name = file.name if file.name != "" else FileService.get_name_from_path(url_address_parser.path)
        file.save()
