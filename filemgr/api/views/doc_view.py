import os

from rest_framework.schemas import get_schema_view

SchemaView = get_schema_view(
    title='uServer FileMgr API',
    description="File management API for multiple storages/users",
    version="1.0.0",
    url='{}/api/'.format(os.environ['VIRTUAL_HOST'])
)
