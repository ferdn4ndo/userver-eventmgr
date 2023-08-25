from api.pagination.base_pagination import BasePagination


class LargeResultsSetPagination(BasePagination):
    default_limit = 100
    max_limit = 1000
