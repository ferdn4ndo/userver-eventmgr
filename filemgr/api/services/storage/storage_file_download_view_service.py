import datetime
import math
import os

from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.request import Request

from api.models import get_object_or_404
from api.serializers.storage.storage_file_download_serializer import StorageFileDownloadSerializer
from core.models import StorageFile, Storage
from core.services.storage.storage_file_service import StorageFileService


class StorageFileDownloadViewService:
    @staticmethod
    def compute_download_expiration_seconds_from_size(file_size_bytes: int) -> int:
        """
        Gets a download expiration datetime for a given file based on a calculation on it's size.

        Adjust this value by altering the env DOWNLOAD_EXP_BYTES_SECS_RATIO.
        We recommend values between 4 and 5.

        The lowest size considered in the calculation is 100.000 bytes

        Some examples:

        Ratio   | Size                        | Time delta
        --------|-----------------------------|---------------------
        4       | 1872566538 bytes (1.74 GB)  | 7392 secs (2:03:12)
        4       | 108360999 bytes (103 MB)    | 4168 secs (1:09:28)
        4       | 156144 bytes (152 KB)       | 727 secs (0:12:07)
        --------|-----------------------------|---------------------
        4.25    | 1872566538 bytes (1.74 GB)  | 12899 secs (3:34:59)
        4.25    | 108360999 bytes (103 MB)    | 7017 secs (1:56:57)
        4.25    | 156144 bytes (152 KB)       | 1098 secs (0:18:18)
        --------|-----------------------------|---------------------
        4.5     | 1872566538 bytes (1.74 GB)  | 22509 secs (6:15:09)
        4.5     | 108360999 bytes (103 MB)    | 11814 secs (3:16:54)
        4.5     | 156144 bytes (152 KB)       | 1657 secs (0:27:37)
        --------|-----------------------------|---------------------
        4.75    | 1872566538 bytes (1.74 GB)  | 39280 secs (10:54:40)
        4.75    | 108360999 bytes (103 MB)    | 19891 secs (5:31:31)
        4.75    | 156144 bytes (152 KB)       | 2503 secs (0:41:43)
        --------|-----------------------------|---------------------
        5       | 1872566538 bytes (1.74 GB)  | 68544 secs (19:02:24)
        5       | 108360999 bytes (103 MB)    | 33488 secs (9:18:08)
        5       | 156144 bytes (152 KB)       | 3778 secs (0:12:07)
        --------|-----------------------------|---------------------

        :return:
        """
        lower_threshold = 100000
        bytes_to_secs_ratio = float(os.getenv('DOWNLOAD_EXP_BYTES_SECS_RATIO', '4.25'))
        file_size = lower_threshold if file_size_bytes < lower_threshold else file_size_bytes
        secs = round(math.pow(math.log(file_size, 10), bytes_to_secs_ratio))

        return secs

    @staticmethod
    def create_download_link_from_request(request: Request, storage_id: str, file_id: str) -> JsonResponse:
        storage = get_object_or_404(Storage.objects.all(), id=storage_id)
        storage_file = get_object_or_404(
            StorageFile.create_storage_queryset(user=request.user, storage=storage),
            id=file_id
        )

        request.data['storage_file'] = storage_file.id
        request.data['owner'] = request.user.id

        expiration_seconds = StorageFileDownloadViewService.compute_download_expiration_seconds_from_size(
            file_size_bytes=storage_file.size
        )
        expiration_timestamp = timezone.now() + datetime.timedelta(seconds=expiration_seconds)
        request.data['expires_at'] = expiration_timestamp

        serializer = StorageFileDownloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        storage_file_download = serializer.save()

        validated_data = serializer.validated_data
        force_download = validated_data['force_download'] if 'force_download' in validated_data else False

        driver = StorageFileService(storage_file=storage_file).load_driver()
        download_url = driver.get_download_url(
            file=storage_file,
            expiration_seconds=expiration_seconds,
            force_download=force_download,
        )

        storage_file_download.download_url = download_url
        storage_file_download.save()

        serializer = StorageFileDownloadSerializer(storage_file_download)

        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
