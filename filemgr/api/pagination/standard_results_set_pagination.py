from api.pagination.base_pagination import BasePagination


class StandardResultsSetPagination(BasePagination):
    default_limit = 10
    max_limit = 100
