class ServiceError(Exception):
    """Base class for service-layer (domain) errors."""


class ValidationError(ServiceError):
    """Invalid input or business rule violation (HTTP 400)."""


class NotFoundError(ServiceError):
    """Requested resource not found (HTTP 404)."""


class ConflictError(ServiceError):
    """State conflict, e.g., already finalized (HTTP 409)."""


class ExternalServiceError(ServiceError):
    """Upstream/external dependency error (HTTP 502)."""


class DependencyError(ServiceError):
    """Internal dependency (DB, repository) error (HTTP 503)."""

