from __future__ import annotations

import json
import shutil

import requests
from typing import Dict, Any

from api.exceptions.precondition_failed_exception import PreconditionFailedException


class WebRequest:

    REQUEST_METHODS = [
        'POST',
        'GET',
        'PUT',
        'PATCH',
        'DELETE',
        'HEAD',
        'OPTIONS'
    ]

    USER_AGENT = 'uServer FileMgr WebRequest 1.0.0'

    def __init__(
            self,
            url: str = None,
            method: str = 'GET',
            headers: Dict = None,
            payload: Dict = None,
            stream: bool = False
    ):
        self.url = url
        self.headers = {
            'User-Agent': self.USER_AGENT
        }
        if headers is not None:
            self.headers = {**self.headers, **headers}

        self._parse_method(method=method)

        self.payload = payload
        self.stream = stream

        self.object = None
        self._update_object()

    def _parse_method(self, method: str) -> None:
        method = str(method).upper()

        if method is not None and method not in self.REQUEST_METHODS:
            raise PreconditionFailedException('The method must be one of the followings: {} ({} given)')

        self.method = method

    def set_json_payload(self, payload=None) -> WebRequest:
        payload = payload if payload is not None else {}
        self.headers['Content-Type'] = 'application/json'
        self.payload = json.dumps(payload)
        self._update_object()
        return self

    def _update_object(self):
        """
        Update the requests object with the class arguments
        :return:
        """
        request_init = getattr(requests, str(self.method).lower())
        self.object = request_init(self.url, headers=self.headers, data=self.payload, stream=self.stream)

    def get_raw(self) -> Any:
        """
        Returns the raw response from the request
        :return:
        """
        if self.object is None:
            return None

        return self.object.raw

    @staticmethod
    def get_url_info(url: str, headers=None):
        """
        Retrieves the HEAD information about a given URL
        :param url:
        :param headers:
        :return:
        """
        response = WebRequest(url=url, method='HEAD', headers=headers)

        return response.object.headers

    def get_json_response(self):
        """
        Retrieves the JSON parsed response from the requests object
        :return:
        """
        return None if self.object is None else self.object.json()

    def get_status_code(self):
        """
        Retrieves the HTTP response status code from the requests object
        :return:
        """
        return None if self.object is None else self.object.status_code

    def download_to(self, dest_filename: str) -> str:
        """
        Downloads the request response to a given filename
        :param dest_filename:
        :return:
        """
        self._update_object()

        with self.object(self.url, headers=self.headers, data=self.payload, stream=True) as req:
            with open(dest_filename, 'wb') as file:
                shutil.copyfileobj(req.raw, file)

        return dest_filename
