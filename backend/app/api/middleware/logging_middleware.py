"""
SPARK — Request Logging Middleware
Logs every incoming request with method, path, status code,
duration, and request ID. Attaches request ID to structlog
context so every log within a request is traceable.
"""

import time
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = structlog.get_logger(__name__)

# Header name for request tracing
REQUEST_ID_HEADER = "X-Request-ID"

# Paths excluded from access logging (noisy health checks)
_SKIP_LOG_PATHS = {"/api/v1/health", "/api/v1/health/ready"}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Generates or extracts a unique request ID
    2. Binds request ID to structlog context (so all logs within request include it)
    3. Logs request start and completion with timing
    4. Attaches X-Request-ID to the response header
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate unique request ID (accept from upstream if provided)
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())

        # Bind to structlog context — all downstream logs will include this
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        start_time = time.perf_counter()

        # Skip verbose logging for health check endpoints
        should_log = request.url.path not in _SKIP_LOG_PATHS

        if should_log:
            logger.info(
                "Request started",
                query_params=str(request.query_params) if request.query_params else None,
            )

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                "Request failed with unhandled exception",
                duration_ms=duration_ms,
                error=str(exc),
            )
            raise

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        if should_log:
            log_fn = logger.warning if response.status_code >= 400 else logger.info
            log_fn(
                "Request completed",
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

        # Attach request ID to response for client traceability
        response.headers[REQUEST_ID_HEADER] = request_id

        # Clear context after request completes
        structlog.contextvars.clear_contextvars()

        return response