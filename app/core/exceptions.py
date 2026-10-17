"""Application domain exception classes."""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundError(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' was not found.",
            code="ENTITY_NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": str(identifier)},
        )


class DuplicateEntityError(AppException):
    """Raised when a resource or idempotent operation conflicts with an existing entity."""

    def __init__(self, resource: str, identifier: Any, message: Optional[str] = None):
        super().__init__(
            message=message or f"{resource} with identifier '{identifier}' already exists.",
            code="DUPLICATE_ENTITY",
            status_code=409,
            details={"resource": resource, "identifier": str(identifier)},
        )


class InvalidInputError(AppException):
    """Raised when business validation rules fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="INVALID_INPUT",
            status_code=422,
            details=details or {},
        )


class AuthenticationError(AppException):
    """Raised when authentication credentials are missing or invalid."""

    def __init__(self, message: str = "Invalid or expired authentication credentials."):
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=401,
        )


class AuthorizationError(AppException):
    """Raised when an authenticated user does not have required permissions."""

    def __init__(self, message: str = "Insufficient permissions to perform this operation."):
        super().__init__(
            message=message,
            code="PERMISSION_DENIED",
            status_code=403,
        )


class PolicyViolationError(AppException):
    """Raised when an operation violates business or safety policy."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="POLICY_VIOLATION",
            status_code=400,
            details=details or {},
        )


class ModelInferenceError(AppException):
    """Raised when ML classification or inference fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="MODEL_INFERENCE_ERROR",
            status_code=500,
            details=details or {},
        )


class ReplayError(AppException):
    """Raised when historical replay fails or configuration is invalid."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="REPLAY_ERROR",
            status_code=400,
            details=details or {},
        )
