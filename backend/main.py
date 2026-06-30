"""
SPARK — Main Application Entry Point
FastAPI application with complete middleware stack and all routes registered.
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.core.config import get_settings
from app.core.events import lifespan
from app.core.exceptions import SPARKException
from app.core.logging import get_logger, setup_logging
from app.models.common import error_response

# Initialize structured logging first — before anything else loads
setup_logging()
logger = get_logger(__name__)

settings = get_settings()


def create_application() -> FastAPI:
    """
    Application factory — creates and configures the FastAPI instance.
    """
    application = FastAPI(
        title="SPARK API",
        description="Autonomous Completion Intelligence System — Backend API",
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # -------------------------------------------------------
    # Middleware Stack
    # Order matters: first added = outermost = runs first on request,
    # last on response.
    # -------------------------------------------------------

    # CORS — must be outermost to handle preflight OPTIONS correctly
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    # Request logging — logs every request with timing and request ID
    from app.api.middleware.logging_middleware import RequestLoggingMiddleware

    application.add_middleware(RequestLoggingMiddleware)

    # -------------------------------------------------------
    # Exception Handlers
    # -------------------------------------------------------
    _register_exception_handlers(application)

    # -------------------------------------------------------
    # Routes
    # -------------------------------------------------------
    _register_routes(application)

    logger.info(
        "SPARK application created",
        env=settings.APP_ENV,
        routes_registered=True,
    )

    return application


def _register_exception_handlers(application: FastAPI) -> None:
    """Register global exception handlers for consistent error responses."""

    @application.exception_handler(SPARKException)
    async def spark_exception_handler(
        request: Request, exc: SPARKException
    ) -> JSONResponse:
        """
        Handles all custom SPARK exceptions.
        Converts domain exceptions to HTTP responses with consistent format.
        """
        logger.warning(
            "SPARK exception caught",
            code=exc.code,
            message=exc.message,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.http_status,
            content=error_response(
                code=exc.code,
                message=exc.message,
                details=exc.details,
            ),
        )

    @application.exception_handler(PydanticValidationError)
    async def pydantic_validation_handler(
        request: Request, exc: PydanticValidationError
    ) -> JSONResponse:
        """
        Handles Pydantic validation errors from request body parsing.
        Returns field-level error details.
        """
        logger.warning(
            "Pydantic validation error",
            path=request.url.path,
            errors=exc.error_count(),
        )
        return JSONResponse(
            status_code=422,
            content=error_response(
                code="VALIDATION_ERROR",
                message="Request validation failed",
                details=exc.errors(),
            ),
        )

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """
        Catch-all for unhandled exceptions.
        Logs the full exception for debugging.
        Returns a generic 500 without leaking internals to the client.
        """
        logger.error(
            "Unhandled exception",
            path=request.url.path,
            error=str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content=error_response(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred. Our team has been notified.",
            ),
        )


def _register_routes(application: FastAPI) -> None:
    """Register all API route modules under /api/v1."""
    from app.api.routes import (
        agents,
        analytics,
        bankruptcy,
        cms,
        genome,
        health,
        interventions,
        milestones,
        tasks,
        users,
        webhooks,
    )

    api_prefix = "/api/v1"

    # Health — no auth required
    application.include_router(health.router, prefix=api_prefix)

    # Webhooks — internal, no user auth
    application.include_router(webhooks.router, prefix=api_prefix)

    # Protected user routes
    application.include_router(users.router, prefix=api_prefix, tags=["Users"])
    application.include_router(tasks.router, prefix=api_prefix, tags=["Tasks"])
    application.include_router(
        milestones.router, prefix=api_prefix, tags=["Milestones"]
    )
    application.include_router(cms.router, prefix=api_prefix, tags=["CMS"])
    application.include_router(genome.router, prefix=api_prefix, tags=["Genome"])
    application.include_router(
        interventions.router, prefix=api_prefix, tags=["Interventions"]
    )
    application.include_router(
        analytics.router, prefix=api_prefix, tags=["Analytics"]
    )
    application.include_router(
        bankruptcy.router, prefix=api_prefix, tags=["Bankruptcy"]
    )
    application.include_router(agents.router, prefix=api_prefix, tags=["Agents"])


# Create the application instance
app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.is_development,
        log_config=None,
    )