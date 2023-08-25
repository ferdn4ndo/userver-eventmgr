import magic

from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import filesizeformat
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


@deconstructible
class FileValidator(object):
    """
    Based on sultan-alotaibi @ https://stackoverflow.com/questions/20272579/django-validate-file-type-of-uploaded-file
    """
    error_messages = {
     'max_size': _("Ensure this file size is not greater than {}s (your ir {}s)."),
     'min_size': _("Ensure this file size is not less than {}s (your is {}s)."),
     'content_type': "Files of type {}s are not supported.",
    }

    def __init__(self, max_size=None, min_size=None, content_types=()):
        self.max_size = max_size
        self.min_size = min_size
        self.content_types = content_types

    def __call__(self, data):
        if self.max_size is not None and data.size > self.max_size:
            raise ValidationError(
                self.error_messages['max_size'].format(filesizeformat(self.max_size), filesizeformat(data.size))
            )

        if self.min_size is not None and data.size < self.min_size:
            raise ValidationError(
                self.error_messages['min_size'].format(filesizeformat(self.min_size), filesizeformat(data.size))
            )

        if self.content_types:
            content_type = magic.from_buffer(data.read(), mime=True)
            data.seek(0)

            if content_type not in self.content_types:
                raise ValidationError(
                    self.error_messages['content_type'].format(content_type, ', '.join(self.content_types)),
                )

    def __eq__(self, other):
        return (
            isinstance(other, FileValidator) and
            self.max_size == other.max_size and
            self.min_size == other.min_size and
            self.content_types == other.content_types
        )
