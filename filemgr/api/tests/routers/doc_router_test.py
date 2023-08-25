import requests
from rest_framework import status

from ..generic import GenericTestCase


class DocsRouterOpenAPITest(GenericTestCase.GenericTest):

    def setUp(self) -> None:
        super(DocsRouterOpenAPITest, self).setUp()
        self.endpoint = '/docs/openapi/'

    def test_openapi_return_success_not_logged(self) -> None:
        request = requests.get(self.get_endpoint_full_uri())
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertIn('Content-Type', request.headers)
        content_type = request.headers['Content-Type']
        self.assertEqual(content_type, 'application/vnd.oai.openapi')


class DocsRouterRedocTest(GenericTestCase.GenericTest):

    def setUp(self) -> None:
        super(DocsRouterRedocTest, self).setUp()
        self.endpoint = '/docs/redoc/'

    def test_redoc_return_success_not_logged(self) -> None:
        request = requests.get(self.get_endpoint_full_uri())
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertIn('Content-Type', request.headers)
        content_type = request.headers['Content-Type']
        self.assertEqual(content_type, 'text/html; charset=utf-8')
        self.assertIn('<title>ReDoc</title>', request.text)
