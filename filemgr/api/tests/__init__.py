from .routers.doc_router_test import DocsRouterOpenAPITest, DocsRouterRedocTest

from .views.storage_view_test import \
    StorageViewSetCreateTest, \
    StorageViewSetDestroyTest, \
    StorageViewSetListTest, \
    StorageViewSetRetrieveTest, \
    StorageViewSetPartialUpdateTest

from .views.storage_user_view_test import \
    StorageUserViewSetCreateTest, \
    StorageUserViewSetDestroyTest, \
    StorageUserViewSetRetrieveTest, \
    StorageUserViewSetListTest, \
    StorageUserViewSetPartialUpdateTest

from .views.storage_file_view_test import \
    StorageFileViewSetDestroyTest, \
    StorageFileViewSetRetrieveTest, \
    StorageFileViewSetListTest, \
    StorageFileViewSetPartialUpdateTest

from .views.storage_file_download_view_test import \
    StorageFileDownloadViewSetCreateTest, \
    StorageFileDownloadViewSetListTest, \
    StorageFileDownloadViewSetRetrieveTest

from .views.storage_file_upload_view_test import \
    StorageFileUploadAmazonViewSetCreateTest
    # StorageFileUploadViewSetCreateTest, \
    # StorageFileUploadUrlViewSetCreateTest
