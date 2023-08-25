from rest_framework import routers

from api.routers.route_names import RouteNames
from api.views.storage.storage_media_view import StorageMediaViewSet
from api.views.storage.storage_file_download_view import StorageFileDownloadViewSet
from api.views.storage.storage_file_upload_from_file_view import StorageFileUploadView
from api.views.storage.storage_file_upload_from_url_view import StorageFileUploadUrlView
from api.views.storage.storage_file_view import StorageFileViewSet
from api.views.storage.storage_trash_view import StorageTrashViewSet
from api.views.storage.storage_user_view import StorageUserViewSet
from api.views.storage.storage_view import StorageViewSet

router = routers.SimpleRouter()
router.register(
    prefix=r'',
    viewset=StorageViewSet,
    basename=RouteNames.ROUTE_STORAGE
)
router.register(
    prefix=r'(?P<storage_id>[^/.]+)/files',
    viewset=StorageFileViewSet,
    basename=RouteNames.ROUTE_STORAGE_FILE
)
router.register(
    prefix=r'(?P<storage_id>[^/.]+)/files/(?P<file_id>[^/.]+)/download',
    viewset=StorageFileDownloadViewSet,
    basename=RouteNames.ROUTE_STORAGE_FILE_DOWNLOAD
)
router.register(
    prefix=r'(?P<storage_id>[^/.]+)/media',
    viewset=StorageMediaViewSet,
    basename=RouteNames.ROUTE_STORAGE_MEDIA
)
router.register(
    prefix=r'(?P<storage_id>[^/.]+)/trash',
    viewset=StorageTrashViewSet,
    basename=RouteNames.ROUTE_STORAGE_TRASH
)
router.register(
    prefix=r'(?P<storage_id>[^/.]+)/upload-from-file',
    viewset=StorageFileUploadView,
    basename=RouteNames.ROUTE_STORAGE_UPLOAD_FILE
)
router.register(
    prefix=r'(?P<storage_id>[^/.]+)/upload-from-url',
    viewset=StorageFileUploadUrlView,
    basename=RouteNames.ROUTE_STORAGE_UPLOAD_URL
)
router.register(
    prefix=r'(?P<storage_id>[^/.]+)/users',
    viewset=StorageUserViewSet,
    basename=RouteNames.ROUTE_STORAGE_USER
)
