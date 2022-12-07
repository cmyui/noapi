import enum


class ServiceError(str, enum.Enum):
    RESOURCE_NOT_FOUND = "resource.not_found"
    RESOURCE_FETCH_FAILED = "resource.fetch_failed"
    RESOURCE_CREATION_FAILED = "resource.creation_failed"
    RESOURCE_DELETION_FAILED = "resource.deletion_failed"
    RESOURCE_UPDATE_FAILED = "resource.update_failed"

    # TODO: support for custom ones
    # (e.g. "accounts.username_exists", "avatars.size_too_large")
