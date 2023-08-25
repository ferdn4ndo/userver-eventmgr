import datetime
import os
from typing import Tuple, Optional

from django import http
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header

from app.models.user.user_model import CustomUser, UserToken
from app.services.web_request import WebRequest


class UServerAuthentication(authentication.BaseAuthentication):
    """
    uServer-Auth remote validated token authentication.

    Clients should authenticate by passing the token key in the "Authorization" HTTP header, prepended with the
    string "Bearer ".  For example:

    Authorization: Bearer 401f7ac837da42b97f613d789819ff93537bee6a
    """
    keyword = 'Bearer'

    def get_token_from_request(self, request: http.request) -> Optional[str]:
        """
        Retrieve the token used to authenticate a request
        :param request:
        :return:
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            return auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

    def authenticate(self, request: http.request) -> [Tuple]:
        """
        Authenticate the request and return a two-tuple of (user, token).
        :param request:
        :return: Tuple
        """
        if request.method == 'OPTIONS':
            return AnonymousUser, ''

        token = self.get_token_from_request(request)

        return self.authenticate_credentials(token)

    def analyse_token(self, token: str):
        """
        Performs a checking in uServer-Auth against a given token
        :param token:
        :return: The json response of uServer-Auth
        """
        auth_url = self.get_auth_url()
        request = WebRequest(
            url=auth_url,
            method='GET',
            headers={
                'Authorization': 'Bearer {}'.format(token)
            }
        )
        return request.get_json_response()

    def authenticate_credentials(self, token: str) -> Tuple:
        """
        Validate a given token credential and retrieve a local user account if successful
        :param token:
        :return:
        """
        try:
            user_token = UserToken.objects.get(token=token)

            if user_token.expires_at.astimezone(timezone.utc).replace(tzinfo=None) < datetime.datetime.utcnow():
                raise exceptions.AuthenticationFailed(_("The authentication token has expired. Please log-in again or use the refresh token to retrieve a new one."))

            return user_token.user, token
        except UserToken.DoesNotExist:
            pass

        response_data = self.analyse_token(token)
        if response_data is None:
            raise exceptions.AuthenticationFailed(_("Invalid or malformed token."))
        if 'message' in response_data:
            raise exceptions.AuthenticationFailed(_(response_data['message']))
        if 'uuid' not in response_data:
            raise exceptions.AuthenticationFailed(_(response_data['message']))

        user = UServerAuthentication.create_user_from_response_data(response_data)
        user_token = UserToken(
            token=token,
            user=user,
            issued_at=response_data['token']['issued_at'],
            expires_at=response_data['token']['expires_at'],
        )
        user_token.save()

        return user, token

    def retrieve_auth_user(self, request: http.request, system_name: str, username: str) -> CustomUser:
        """
        Retrieve a single user from the uServer-Auth service
        :param request:
        :param system_name:
        :param username:
        :return:
        """
        token = self.get_token_from_request(request)
        auth_url = self.get_auth_url('systems/{}/users/{}'.format(system_name, username))
        request = WebRequest(
            url=auth_url,
            method='GET',
            headers={'Authorization': 'Bearer {}'.format(token)}
        )

        if request.get_status_code() == 404:
            raise exceptions.NotFound(_('The user {} was not found on system {}!'.format(username, system_name)))

        response_data = request.get_json_response()

        return UServerAuthentication.create_user_from_response_data(response_data)

    @staticmethod
    def create_user_from_response_data(response_data, update_activity=True):
        """
        Create a user (or update the existing one) based on the USever-Auth response data
        :param update_activity:
        :param response_data:
        :return:
        """
        user, created = CustomUser.objects.get_or_create(id=response_data['uuid'])
        user.username = response_data['username']
        user.system_name = response_data['system_name']
        user.is_admin = response_data['is_admin']

        if 'registered_at' in response_data:
            user.registered_at = response_data['registered_at']

        if 'last_activity_at' in response_data and not update_activity:
            user.last_activity_at = response_data['last_activity_at']
        elif update_activity:
            user.last_activity_at = timezone.now()

        user.save()

        return user

    @staticmethod
    def get_auth_url(endpoint: str = 'me') -> str:
        """
        Generates the route to uServer-Auth
        :return: str The route
        """
        return '{}/auth/{}'.format(os.environ['USERVER_AUTH_HOST'], endpoint)

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate` header in a `401 Unauthenticated` response.
        """
        return self.keyword

    @staticmethod
    def clear_cache():
        """
        This will force all users to re-login. Useful when changing/restarting the authentication mechanism, as
        suggested in https://docs.djangoproject.com/en/3.0/topics/auth/customizing/
        :return:
        """
        Session.objects.all().delete()

    def get_user_or_create(self, username: str, password: str):
        """
        Get a user (or create one if not exists) based on a username and password (for the current system)
        :param username:
        :param password:
        :return:
        """
        reg_url = self.get_auth_url('register')
        reg_request = WebRequest(
            url=reg_url,
            method='POST'
        )
        reg_request.set_json_payload({
            'username': username,
            'system_name': os.environ['USERVER_AUTH_SYSTEM_NAME'],
            'system_token': os.environ['USERVER_AUTH_SYSTEM_TOKEN'],
            'password': password
        })
        reg_response = reg_request.get_json_response()

        login_url = self.get_auth_url('login')
        login_request = WebRequest(
            url=login_url,
            method='POST'
        )
        login_request.set_json_payload({
            'username': username,
            'system_name': os.environ['USERVER_AUTH_SYSTEM_NAME'],
            'system_token': os.environ['USERVER_AUTH_SYSTEM_TOKEN'],
            'password': password
        })
        login_response_data = login_request.get_json_response()

        if 'uuid' not in login_response_data:
            raise exceptions.AuthenticationFailed(_("Failed to login with user."))

        return UServerAuthentication.create_user_from_response_data(login_response_data)
