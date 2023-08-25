import os

from django.urls import path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from api.policies.allow_all_policy import AllowAllPolicy
from api.routers.route_names import RouteNames

urlpatterns = [
    path('openapi/', get_schema_view(
        title='uServer FileMgr API',
        description="File management API for multiple storages/users",
        version="1.0.0",
        url='{}/api/'.format(os.environ['VIRTUAL_HOST']),
        permission_classes=[AllowAllPolicy],
        public=True,
    ), name=RouteNames.ROUTE_DOC_OPENAPI),
    path('redoc/', TemplateView.as_view(
        template_name='redoc.html',
        extra_context={'schema_url': RouteNames.ROUTE_DOC_OPENAPI}
    ), name=RouteNames.ROUTE_DOC_REDOC),
]
