from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models.generic_audited_model import GenericAuditedModel
from core.models.storage.storage_model import Storage
from core.models.user.user_model import CustomUser


class StorageUser(GenericAuditedModel):
    """
    Model resource for a storage user relation (users of a storage)
    """

    class StorageUserType(models.TextChoices):
        """
        Enum for the type of storage
        """
        STORAGE_S3 = 'AMAZON_S3', _('Amazon S3')
        STORAGE_LOCAL = 'LOCAL', _('Local')

    storage = models.ForeignKey(to=Storage, on_delete=models.CASCADE)
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    may_write = models.BooleanField(default=False, verbose_name=_("Storage write permission"))
    may_read = models.BooleanField(default=True, verbose_name=_("Storage read permission"))

    @staticmethod
    def user_may_read_storage(user: CustomUser, storage: Storage) -> bool:
        """
        Check if a given user has permission to read a storage. Returns false if no record was found or if any of the
        existing ones have may_read="False" (fail-safe)
        :param user:
        :param storage:
        :return:
        """
        objects = StorageUser.objects.filter(user=user, storage=storage)
        if not len(objects):
            return False

        return all([storage_user.may_read for storage_user in objects])

    @staticmethod
    def user_may_write_storage(user: CustomUser, storage: Storage) -> bool:
        """
        Check if a given user has permission to write to a storage. Returns false if no record was found or if any of
        the existing ones have may_write="False" (fail-safe). Any admin can write to any storage.
        :param user:
        :param storage:
        :return:
        """
        if user.is_admin:
            return True

        objects = StorageUser.objects.filter(user=user, storage=storage)
        if not len(objects):
            return False

        return all([storage_user.may_write for storage_user in objects])
