from rest_framework import status
from rest_framework.test import force_authenticate, APIRequestFactory

from app.services.translation import Messages
from app.tests import dataset

from .generic_test_case import GenericTestCase


class GenericCreateTestCases:

    class CreateTest(GenericTestCase.GenericTest):
        request_args = {}
        payload_valid = None
        payload_invalid = None
        request_data_format = 'json'  # or multipart

        def test_create_success(self) -> None:
            self.check_pre_conditions()
            request = APIRequestFactory().request()
            request.method = request.POST
            request.data = self.payload_valid
            request.META['Content-Type'] = 'application/json'
            #request = self.factory.post(self.endpoint, self.payload_valid, format=self.request_data_format)
            #force_authenticate(request, user=self.user)
            #view = self.view.as_view({'post': 'create'})
            view = self.view.as_view({'post': 'create'})
            response = view(request, **self.request_args)
            response.render()
            self.check_http_response(response=response, expected_code=status.HTTP_201_CREATED)
            self.check_single_resource_response(request=request, response_data=response.data)

        def test_create_fail_not_logged(self) -> None:
            self.check_pre_conditions()
            request = self.factory.post(self.endpoint, self.payload_valid, format=self.request_data_format)
            view = self.view.as_view({'post': 'create'})
            response = view(request, **self.request_args)
            response.render()
            self.check_http_response(
                response=response,
                expected_code=status.HTTP_401_UNAUTHORIZED,
                expected_message=Messages.MSG_NOT_AUTHENTICATED
            )

        def test_create_fail_not_admin(self) -> None:
            if not self.requires_admin:
                self.skipTest("No admin authorization level needed")

            self.check_pre_conditions()
            user_not_admin = dataset.create_user(is_admin=False)
            request = self.factory.post(self.endpoint, self.payload_valid, format=self.request_data_format)
            force_authenticate(request, user=user_not_admin)
            view = self.view.as_view({'post': 'create'})
            response = view(request, **self.request_args)
            response.render()
            self.check_http_response(
                response=response,
                expected_code=status.HTTP_403_FORBIDDEN,
                expected_message=Messages.MSG_NOT_ENOUGH_PERMS
            )

        def test_create_fail_bad_request(self) -> None:
            if self.payload_invalid is None:
                self.skipTest("No invalid payload")

            self.check_pre_conditions()
            request = self.factory.post(self.endpoint, self.payload_invalid, format=self.request_data_format)
            force_authenticate(request, user=self.user)
            view = self.view.as_view({'post': 'create'})
            response = view(request, **self.request_args)
            response.render()
            self.check_http_response(
                response=response,
                expected_code=status.HTTP_400_BAD_REQUEST,
                expected_message=Messages.MSG_ONE_OR_MORE_ERRORS_OCCURRED
            )
