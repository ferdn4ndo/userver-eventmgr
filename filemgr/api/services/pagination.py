from collections import OrderedDict

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class CustomPagination(LimitOffsetPagination):
    KEY_LIMIT = 'limit'
    KEY_OFFSET = 'offset'
    KEY_ITEMS = 'items'
    KEY_COUNT = 'count'
    KEY_LINKS = '_links'
    KEY_LINKS_SELF = 'self'
    KEY_LINKS_NEXT = 'next'
    KEY_LINKS_PREVIOUS = 'previous'
    KEY_LINKS_HREF = 'href'

    limit_query_param = KEY_LIMIT
    offset_query_param = KEY_OFFSET

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            (self.KEY_ITEMS, data),
            (self.KEY_COUNT, self.count),
            (self.KEY_LINKS, self.get_pagination_links()),
        ]))

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                self.KEY_ITEMS: schema,
                self.KEY_COUNT: {
                    'type': 'integer',
                    'example': 123,
                },
                self.KEY_LINKS: {
                    'type': 'object',
                    'properties': {
                        self.KEY_LINKS_SELF: {
                            'type': 'object',
                            'properties': {
                                self.KEY_LINKS_HREF: {
                                    'type': 'string',
                                    'format': 'uri',
                                    'nullable': True,
                                }
                            }
                        },
                        self.KEY_LINKS_NEXT: {
                            'type': 'object',
                            'properties': {
                                self.KEY_LINKS_HREF: {
                                    'type': 'string',
                                    'format': 'uri',
                                    'nullable': True,
                                }
                            }
                        },
                        self.KEY_LINKS_PREVIOUS: {
                            'type': 'object',
                            'properties': {
                                self.KEY_LINKS_HREF: {
                                    'type': 'string',
                                    'format': 'uri',
                                    'nullable': True,
                                }
                            }
                        },
                    }
                },
            },
        }

    def get_pagination_links(self):
        links = {
            **self.get_self_link(),
            **self.get_next_link(),
            **self.get_previous_link(),
        }
        return links

    def get_next_link(self):
        next_url = super(CustomPagination, self).get_next_link()

        if not next_url:
            return {}

        return {self.KEY_LINKS_NEXT: {self.KEY_LINKS_HREF: next_url}}

    def get_previous_link(self):
        previous_url = super(CustomPagination, self).get_next_link()

        if not previous_url:
            return {}

        return {self.KEY_LINKS_PREVIOUS: {self.KEY_LINKS_HREF: previous_url}}

    def get_self_link(self):
        return {self.KEY_LINKS_SELF: {self.KEY_LINKS_HREF: self.request.build_absolute_uri()}}


class LargeResultsSetPagination(CustomPagination):
    default_limit = 100
    max_limit = 1000


class StandardResultsSetPagination(CustomPagination):
    default_limit = 10
    max_limit = 100
