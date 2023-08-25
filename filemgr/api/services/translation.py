from django.utils.translation import gettext_lazy as _


class Messages:
    MSG_NO_STORAGE_READ_PERM = _("You don't have read permissions on this storage.")
    MSG_NO_STORAGE_WRITE_PERM = _("You don't have write permissions on this storage.")
    MSG_NO_FILE_DOWNLOAD_PERM = _("You don't have enough permissions to download this file.")
    MSG_MISSING_FILE_FIELD_FORM = _("Missing file field in form data.")
    MSG_DOWNLOAD_EXPIRED = _("This download link has expired.")
    MSG_NOT_ENOUGH_PERMS = _("You don't have the required level of permissions to access this resource.")
    MSG_NOT_FOUND = _("The request resource wasn't found. Please double-check the identifiers.")
    MSG_NOT_AUTHENTICATED = _("You must be authenticated to perform the requested operation.")
    MSG_INVALID_INPUT_DATA = _("You have supplied malformed/invalid request data.")
    MSG_ONE_OR_MORE_ERRORS_OCCURRED = _("One or more validation error occurred while handling the supplied data.")
    MSG_INVALID_AUTH_SERVICE_RESP = _("Invalid authentication service response.")
    MGS_INVALID_PATH = _("The informed path contains invalid characters. Please use only the set: A-Za-z0-9_-./")
    MGS_FILE_EXISTS_NO_OVERWRITE = _("The file already exists and overwriting is disabled.")
