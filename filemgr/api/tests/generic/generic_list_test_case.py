from rest_framework import status
from rest_framework.test import force_authenticate

from app.services.translation import Messages
from app.tests import dataset
from app.views import GenericModelViewSet

from .generic_test_case import GenericTestCase


class GenericListTestCase:

    class ListTest(GenericTestCase.GenericTest):
        view: GenericModelViewSet or None
        request_args = {}
        expected_items: int

        def test_list_success(self) -> None:
            self.check_pre_conditions()
            request = self.factory.get(self.endpoint)
            force_authenticate(request, user=self.user)
            view = self.view.as_view({'get': 'list'})
            response = view(request=request, **self.request_args)
            response.render()
            self.check_http_response(response=response, expected_code=status.HTTP_200_OK)
            self.check_list_resource_response(
                request=request,
                response_data=response.data,
                expected_count=self.expected_items
            )

        def test_list_fail_not_logged(self) -> None:
            self.check_pre_conditions()
            request = self.factory.get(self.endpoint)
            view = self.view.as_view({'get': 'list'})
            response = view(request=request, **self.request_args)
            response.render()
            self.check_http_response(
                response=response,
                expected_code=status.HTTP_401_UNAUTHORIZED,
                expected_message=Messages.MSG_NOT_AUTHENTICATED
            )

        def test_list_fail_not_admin(self) -> None:
            if not self.requires_admin:
                self.skipTest("No admin authorization level needed")

            self.check_pre_conditions()
            user_not_admin = dataset.create_user(is_admin=False)
            request = self.factory.get(self.endpoint)
            force_authenticate(request, user=user_not_admin)
            view = self.view.as_view({'get': 'list'})
            response = view(request=request, **self.request_args)
            response.render()
            self.check_http_response(
                response=response,
                expected_code=status.HTTP_403_FORBIDDEN,
                expected_message=Messages.MSG_NOT_ENOUGH_PERMS
            )
