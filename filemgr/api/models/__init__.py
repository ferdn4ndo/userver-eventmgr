from django.db.models import QuerySet

from api.exceptions.not_found_exception import NotFoundException


def get_object_or_404(queryset: QuerySet, *args, **kwargs):
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise NotFoundException
