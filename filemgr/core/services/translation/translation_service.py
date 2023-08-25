from django.utils.translation import gettext_lazy as _


class Messages:
    MGS_INVALID_PATH = _("The informed path contains invalid characters. Please use only the set: A-Za-z0-9_-./")
    MSG_CONFLICT = _("The requested operation failed due to a conflicting condition.")
    MSG_PRECONDITION_FAILED = _("The requested operation failed due to a precondition that has failed.")
    MSG_DOWNLOAD_EXPIRED = _("This download link has expired.")
    MSG_EMAIL_ALREADY_REGISTERED = _("The given e-mail is already registered to another user.")
    MSG_EMAIL_ALREADY_VALIDATED = _("Your e-mail address was already validated.")
    MSG_EMAIL_SUCCESSFULLY_VALIDATED = _("Your e-mail address was successfully validated.")
    MSG_EMAIL_VALIDATION_HASH_SENT = _(
        "A confirmation code was sent to your e-mail address. Remember to check your SPAM folder."
    )
    MSG_EVENT_ALREADY_SUBSCRIBED = _("You're already subscribed to this event.")
    MSG_EVENT_NOT_OPEN_FOR_SUBSCRIPTIONS = _("The selected event is not open for subscriptions.")
    MGS_FILE_EXISTS_NO_OVERWRITE = _("The file already exists in the storage and overwriting is not allowed.")
    MSG_INVALID_AUTH_SERVICE_RESP = _("Invalid authentication service response.")
    MSG_INVALID_EMAIL_VALIDATION_HASH = _("The provided e-mail validation hash is invalid.")
    MSG_INVALID_INPUT_DATA = _("You have supplied malformed/invalid request data.")
    MSG_MISSING_FILE_FIELD_FORM = _("Missing file field in form data.")
    MSG_NO_FILE_READ_PERM = _("You don't have enough permissions to read this file.")
    MSG_NO_FILE_DOWNLOAD_PERM = _("You don't have enough permissions to download this file.")
    MSG_NO_STORAGE_READ_PERM = _("You don't have read permissions on this storage.")
    MSG_NO_STORAGE_WRITE_PERM = _("You don't have write permissions on this storage.")
    MSG_NOT_AUTHENTICATED = _("You must be authenticated to perform the requested operation.")
    MSG_NOT_ENOUGH_PERMS = _("You don't have the required level of permissions to perform the requested operation.")
    MSG_NOT_FOUND = _("The request resource wasn't found. Please double-check the identifiers.")
    MSG_ONE_OR_MORE_ERRORS_OCCURRED = _("One or more validation error occurred while handling the supplied data.")
    MSG_SUBSCRIPTION_NOT_ELIGIBLE = _("You don't have all the required conditions to subscribe.")
    MSG_INTERNAL_ERROR = _("An internal error occurred on your system while processing your request. Please try again "
                           "later.")
    MSG_TO_BE_IMPLEMENTED = _("To be implemented.")
