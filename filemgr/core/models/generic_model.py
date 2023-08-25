import uuid

from django.db import models


class GenericModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class Meta:
        abstract = True

    def __str__(self):
        return '%s object (%s)' % (self.__class__.__name__, self.id)
