"""
SPARK — Custom Exception Hierarchy
All domain exceptions inherit from SPARKException.
HTTP status codes are mapped here so the global handler
can convert any exception to the correct HTTP response
without domain logic leaking into the HTTP layer.
"""

from typing import Any


class SPARKException(Exception):
    """Base exception for all SPARK application errors."""

    http_status: int = 500

    def __init__(
        self,
        message: str,
        code: str = "SPARK_ERROR",
        details: Any = None,
    ) -> None:
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


# -------------------------------------------------------
# Authentication & Authorization
# -------------------------------------------------------


class AuthenticationError(SPARKException):
    """Raised when token verification fails."""

    http_status = 401

    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message=message, code="AUTHENTICATION_ERROR")


class AuthorizationError(SPARKException):
    """Raised when user lacks permission for an action."""

    http_status = 403

    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(message=message, code="AUTHORIZATION_ERROR")


# -------------------------------------------------------
# Resource Errors
# -------------------------------------------------------


class NotFoundError(SPARKException):
    """Raised when a requested resource does not exist."""

    http_status = 404

    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            message=f"{resource} with ID '{resource_id}' not found",
            code="NOT_FOUND",
            details={"resource": resource, "id": resource_id},
        )


class ConflictError(SPARKException):
    """Raised when an operation conflicts with existing state."""

    http_status = 409

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message=message, code="CONFLICT", details=details)


class ValidationError(SPARKException):
    """Raised when business validation fails (beyond Pydantic)."""

    http_status = 400

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message=message, code="VALIDATION_ERROR", details=details)


class RateLimitError(SPARKException):
    """Raised when rate limit is exceeded."""

    http_status = 429

    def __init__(self) -> None:
        super().__init__(
            message="Rate limit exceeded. Please slow down.",
            code="RATE_LIMIT_EXCEEDED",
        )


# -------------------------------------------------------
# Task Domain Errors
# -------------------------------------------------------


class TaskNotFoundError(NotFoundError):
    """Raised when a task cannot be found."""

    def __init__(self, task_id: str) -> None:
        super().__init__(resource="Task", resource_id=task_id)


class MilestoneNotFoundError(NotFoundError):
    """Raised when a milestone cannot be found."""

    def __init__(self, milestone_id: str) -> None:
        super().__init__(resource="Milestone", resource_id=milestone_id)


class TaskAlreadyCompletedError(SPARKException):
    """Raised when attempting to modify a completed task."""

    http_status = 409

    def __init__(self, task_id: str) -> None:
        super().__init__(
            message=f"Task '{task_id}' is already completed",
            code="TASK_ALREADY_COMPLETED",
            details={"task_id": task_id},
        )


# -------------------------------------------------------
# User Domain Errors
# -------------------------------------------------------


class UserNotFoundError(NotFoundError):
    """Raised when a user cannot be found."""

    def __init__(self, user_id: str) -> None:
        super().__init__(resource="User", resource_id=user_id)


class GenomeNotInitializedError(SPARKException):
    """Raised when Completion Genome has not been created yet."""

    http_status = 404

    def __init__(self, user_id: str) -> None:
        super().__init__(
            message=f"Completion Genome not initialized for user '{user_id}'",
            code="GENOME_NOT_INITIALIZED",
            details={"user_id": user_id},
        )


# -------------------------------------------------------
# AI / Agent Errors
# -------------------------------------------------------


class AgentError(SPARKException):
    """Raised when an agent fails to complete its task."""

    http_status = 503

    def __init__(self, agent_name: str, message: str, details: Any = None) -> None:
        super().__init__(
            message=f"Agent '{agent_name}' failed: {message}",
            code="AGENT_ERROR",
            details={"agent": agent_name, **(details or {})},
        )


class GeminiError(SPARKException):
    """Raised when Gemini API returns an error or malformed response."""

    http_status = 503

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(
            message=f"Gemini error: {message}",
            code="GEMINI_ERROR",
            details=details,
        )


class GeminiResponseParseError(GeminiError):
    """Raised when Gemini response cannot be parsed into expected format."""

    def __init__(self, raw_response: str) -> None:
        super().__init__(
            message="Failed to parse Gemini response as valid JSON",
            details={"raw_response": raw_response[:500]},
        )


# -------------------------------------------------------
# External Integration Errors
# -------------------------------------------------------


class GoogleAPIError(SPARKException):
    """Raised when a Google API call fails."""

    http_status = 503

    def __init__(self, service: str, message: str, details: Any = None) -> None:
        super().__init__(
            message=f"Google {service} API error: {message}",
            code="GOOGLE_API_ERROR",
            details={"service": service, **(details or {})},
        )


class CalendarError(GoogleAPIError):
    """Raised when Google Calendar API fails."""

    def __init__(self, message: str) -> None:
        super().__init__(service="Calendar", message=message)


class GmailError(GoogleAPIError):
    """Raised when Gmail API fails."""

    def __init__(self, message: str) -> None:
        super().__init__(service="Gmail", message=message)


class GoogleDocsError(GoogleAPIError):
    """Raised when Google Docs API fails."""

    def __init__(self, message: str) -> None:
        super().__init__(service="Docs", message=message)


# -------------------------------------------------------
# Infrastructure Errors
# -------------------------------------------------------


class DatabaseError(SPARKException):
    """Raised when a database operation fails."""

    http_status = 500

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(
            message=f"Database error: {message}",
            code="DATABASE_ERROR",
            details=details,
        )


class CloudTasksError(SPARKException):
    """Raised when Cloud Tasks enqueue fails."""

    http_status = 500

    def __init__(self, message: str) -> None:
        super().__init__(
            message=f"Cloud Tasks error: {message}",
            code="CLOUD_TASKS_ERROR",
        )


class ServiceUnavailableError(SPARKException):
    """Raised when a required service is temporarily unavailable."""

    http_status = 503

    def __init__(self, service: str) -> None:
        super().__init__(
            message=f"Service '{service}' is temporarily unavailable",
            code="SERVICE_UNAVAILABLE",
            details={"service": service},
        )