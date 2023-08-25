from rest_framework import status
from rest_framework.test import force_authenticate

from app.services.translation import Messages
from app.tests import dataset
from app.views import GenericModelViewSet

from .generic_test_case import GenericTestCase


class GenericPartialUpdateTestCase:

    class PartialUpdateTest(GenericTestCase.GenericTest):
        view: GenericModelViewSet or None = None
        request_args = {}
        model_real_id = None
        model_fake_id = None
        payload_valid = None
        payload_invalid = None

        def test_patch_success(self) -> None:
            self.check_pre_conditions()
            endpoint = "{}{}/".format(self.endpoint, self.model_real_id)
            request = self.factory.patch(endpoint, self.payload_valid, format='json')
            self.request_args['pk'] = self.model_real_id
            force_authenticate(request, user=self.user)
            view = self.view.as_view({'patch': 'partial_update'})
            response = view(request, **self.request_args)
            response.render()
            self.check_http_response(response=response, expected_code=status.HTTP_200_OK)
            self.check_single_resource_response(request=request, response_data=response.data)

        def test_patch_fail_not_logged(self) -> None:
            self.check_pre_conditions()
            endpoint = "{}{}/".format(self.endpoint, self.model_real_id)
            request = self.factory.patch(endpoint, self.payload_valid, format='json')
            self.request_args['pk'] = self.model_real_id
            view = self.view.as_view({'patch': 'partial_update'})
            response = view(request, **self.request_args)
            response.render()
            self.check_http_response(
                response=response,
                expected_code=status.HTTP_401_UNAUTHORIZED,
                expected_message=Messages.MSG_NOT_AUTHENTICATED
            )

        def test_patch_fail_not_admin(self) -> None:
            if not self.requires_admin:
                self.skipTest("No admin authorization level needed")

            self.check_pre_conditions()
            user_not_admin = dataset.create_user(is_admin=False)
            endpoint = "{}{}/".format(self.endpoint, self.model_real_id)
            request = self.factory.patch(endpoint, self.payload_valid, format='json')
            self.request_args['pk'] = self.model_real_id
            force_authenticate(request, user=user_not_admin)
            view = self.view.as_view({'patch': 'partial_update'})
            response = view(request, **self.request_args)
            response.render()
            self.check_http_response(
                response=response,
                expected_code=status.HTTP_403_FORBIDDEN,
                expected_message=Messages.MSG_NOT_ENOUGH_PERMS
            )

        def test_patch_fail_bad_request(self) -> None:
            if self.payload_invalid is None:
                self.skipTest("No invalid payload")

            self.check_pre_conditions()
            endpoint = "{}{}/".format(self.endpoint, self.model_real_id)
            request = self.factory.patch(endpoint, self.payload_invalid, format='json')
            self.request_args['pk'] = self.model_real_id
            force_authenticate(request, user=self.user)
            view = self.view.as_view({'patch': 'partial_update'})
            response = view(request, **self.request_args)
            response.render()
            self.check_http_response(
                response=response,
                expected_code=status.HTTP_400_BAD_REQUEST,
                expected_message=Messages.MSG_ONE_OR_MORE_ERRORS_OCCURRED
            )

        def test_patch_fail_not_found(self) -> None:
            if not self.model_fake_id:
                self.skipTest("No model_fake_id argument given")

            self.check_pre_conditions()
            endpoint = "{}{}/".format(self.endpoint, self.model_fake_id)
            request = self.factory.patch(endpoint, self.payload_valid, format='json')
            self.request_args['pk'] = self.model_fake_id
            force_authenticate(request, user=self.user)
            view = self.view.as_view({'patch': 'partial_update'})
            response = view(request, **self.request_args)
            response.render()
            self.check_http_response(
                response=response,
                expected_code=status.HTTP_404_NOT_FOUND,
                expected_message=Messages.MSG_NOT_FOUND
            )
