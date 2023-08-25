import datetime
import os
from typing import Tuple, Dict

from django import http
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication
from rest_framework.authentication import get_authorization_header

from api.exceptions.not_authenticated_exception import NotAuthenticatedException
from core.exceptions.model_not_found_exception import ModelNotFoundException
from core.models.user.user_model import CustomUser
from core.models.user.user_token_model import UserToken
from core.services.logger.logger_service import get_logger
from core.services.web_request.web_request_service import WebRequestService


class UServerAuthenticationService(authentication.BaseAuthentication):
    """
    uServer-Auth remote validated token authentication.

    Clients should authenticate by passing the token key in the "Authorization" HTTP header, prepended with the
    string "Token ".  For example:

    Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """
    keyword = 'Token'

    def __init__(self):
        self.logger = get_logger(__name__)

    def authenticate(self, request: http.request) -> tuple:
        """
        Authenticate the request and return a two-tuple of (user, token).
        :param request:
        :return: Tuple
        """
        auth_parts = get_authorization_header(request).split()

        if not auth_parts:
            self.logger.debug("Invalid token header (no auth header)")

            return None

        self._check_auth_header_parts(auth_parts=auth_parts)

        try:
            token = auth_parts[1].decode()
        except UnicodeError:
            self.logger.debug("Invalid token header (unicode error)")
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise NotAuthenticatedException(msg)

        return self.authenticate_credentials(token)

    def _check_auth_header_parts(self, auth_parts: list) -> None:
        auth_keyword = auth_parts[0].decode('utf-8')
        if auth_keyword.lower() != self.keyword.lower():
            self.logger.debug(f"Invalid token value prefix (expecting '{self.keyword}', got '{auth_keyword}')")

            return None

        if len(auth_parts) == 1:
            self.logger.debug("Invalid token header (auth header words == 1)")
            msg = _('Invalid token header. No credentials provided.')
            raise NotAuthenticatedException(msg)
        elif len(auth_parts) > 2:
            self.logger.debug("Invalid token header (auth header words > 2)")
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise NotAuthenticatedException(msg)

    def analyse_token(self, token: str) -> dict:
        """
        Performs a checking in uServer-Auth against a given token
        :param token:
        :return: The json response of uServer-Auth
        """
        auth_url = self.get_auth_url()
        request = WebRequestService(
            url=auth_url,
            method='GET',
            headers={
                'Authorization': 'Bearer {}'.format(token)
            }
        )
        response_data = request.get_json_response()

        if response_data is None:
            raise NotAuthenticatedException(_("Invalid or malformed token."))
        if 'message' in response_data:
            raise NotAuthenticatedException(_(response_data['message']))
        if 'uuid' not in response_data:
            raise NotAuthenticatedException(_(response_data['message']))

        return response_data

    def authenticate_credentials(self, token: str) -> tuple:
        """
        Validate a given token credential and retrieve a local user account if successful
        :param token:
        :return:
        """
        try:
            user_token = UserToken.objects.get(token=token)

            if user_token.expires_at.astimezone(timezone.utc).replace(tzinfo=None) < datetime.datetime.utcnow():
                raise NotAuthenticatedException(_("The authentication token has expired. Please log-in again or use the refresh token to retrieve a new one."))

            return user_token.user, token
        except UserToken.DoesNotExist:
            pass

        response_data = self.analyse_token(token)

        user = UServerAuthenticationService.create_user_from_email(
            email=response_data['username'],
            system_name=response_data['system_name'],
            is_admin=response_data['is_admin'],
        )
        user_token, created = UserToken.objects.get_or_create(
            token=token,
            user=user,
            issued_at=response_data['token']['issued_at'],
            expires_at=response_data['token']['expires_at'],
        )
        user_token.save()

        return user, token

    @staticmethod
    def create_user_from_email(email: str, system_name: str, is_admin: bool = False) -> CustomUser:
        """
        Create a user (or update the existing one) based on the USever-Auth response data
        :return:
        """
        user, created = CustomUser.objects.get_or_create(username=email)
        user.system_name = system_name
        user.is_admin = is_admin
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

    def get_user_from_system_name_and_username(self, system_name: str, username: str) -> CustomUser:
        """
        Get an existing uServer Auth user based on his uuid
        :param system_name:
        :param username:
        :return:
        """
        admin_login_data = self.perform_login(
            username=os.environ['USERVER_AUTH_USER'],
            password=os.environ['USERVER_AUTH_PASSWORD'],
        )

        access_token = admin_login_data['access_token']

        url = self.get_auth_url(f'systems/{system_name}/users/{username}')

        user_request = WebRequestService(
            url=url,
            method='GET',
            headers={
              'Authorization': f'Bearer {access_token}'
            },
        )
        user_response = user_request.get_json_response()
        status_code = user_request.get_status_code()

        if status_code != 200:
            self.logger.warning(
                f"The user with system_name '{system_name}'"
                f" and username '{username}' returned status"
                f" code {status_code} from uServer-Auth!"
                f" Response Payload: {user_response}"
            )
            raise ModelNotFoundException("The given user was not found!")

        user, created = CustomUser.objects.get_or_create(id=user_response['uuid'])
        user.username = user_response['username']
        user.system_name = user_response['system_name']
        user.is_admin = user_response['is_admin']
        user.save()

        self.logger.debug(
            f"User {'CREATED' if created else 'UPDATED'} from uServerAuth: "
            f"id={user.id}; "
            f"username='{username}'; "
            f"system_name='{system_name}'; "
            f"is_admin='{'true' if user.is_admin else 'false'}'"
        )

        return user

    def perform_registration(self, email: str, password: str) -> Dict:
        reg_url = self.get_auth_url('register')
        reg_request = WebRequestService(
            url=reg_url,
            method='POST'
        )
        reg_request.set_json_payload({
            'username': email,
            'system_name': os.environ['USERVER_AUTH_SYSTEM_NAME'],
            'system_token': os.environ['USERVER_AUTH_SYSTEM_TOKEN'],
            'password': password
        })
        reg_response = reg_request.get_json_response()

        return reg_response

    def perform_login(self, username: str, password: str) -> Dict:
        login_url = self.get_auth_url('login')
        login_request = WebRequestService(
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

        if 'access_token' not in login_response_data:
            raise NotAuthenticatedException(_("Failed to login with user."))

        user, created = CustomUser.objects.get_or_create(username=username)
        user.set_password(password)
        user.save()
        login_response_data['user_id'] = user.id

        return login_response_data
