"""
SPARK — Common Response Models
Defines the consistent API envelope used for every response.
All API responses are wrapped in these models for uniformity.
"""

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
from uuid import uuid4

from pydantic import BaseModel, Field

T = TypeVar("T")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_request_id() -> str:
    return str(uuid4())


class ResponseMeta(BaseModel):
    """Metadata attached to every API response."""

    request_id: str = Field(default_factory=_new_request_id)
    timestamp: str = Field(default_factory=_utc_now_iso)


class SuccessResponse(BaseModel, Generic[T]):
    """
    Standard success response envelope.

    All successful API responses use this structure:
    {
        "success": true,
        "data": <payload>,
        "meta": { "request_id": "...", "timestamp": "..." }
    }
    """

    success: bool = True
    data: T
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


class ErrorDetail(BaseModel):
    """Structured error information."""

    code: str
    message: str
    details: Any = None


class ErrorResponse(BaseModel):
    """
    Standard error response envelope.

    All API errors use this structure:
    {
        "success": false,
        "error": { "code": "...", "message": "...", "details": null },
        "meta": { "request_id": "...", "timestamp": "..." }
    }
    """

    success: bool = False
    error: ErrorDetail
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


def success_response(data: Any, request_id: str | None = None) -> dict[str, Any]:
    """
    Build a success response dictionary.
    Use this helper in route handlers for consistency.
    """
    meta = ResponseMeta(request_id=request_id or _new_request_id())
    return {
        "success": True,
        "data": data,
        "meta": meta.model_dump(),
    }


def error_response(
    code: str,
    message: str,
    details: Any = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    """
    Build an error response dictionary.
    Used by the global exception handler.
    """
    meta = ResponseMeta(request_id=request_id or _new_request_id())
    return {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
        "meta": meta.model_dump(),
    }