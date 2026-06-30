"""
SPARK — Structured Logging Configuration
JSON-structured logging compatible with Google Cloud Logging.
Every log entry includes request context for traceability.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor


def add_service_context(
    logger: Any, method: str, event_dict: EventDict
) -> EventDict:
    """Add SPARK service metadata to every log entry."""
    event_dict["service"] = "spark-backend"
    return event_dict


def rename_event_key(
    logger: Any, method: str, event_dict: EventDict
) -> EventDict:
    """
    Rename 'event' key to 'message' for Cloud Logging compatibility.
    Cloud Logging expects 'message' as the primary log field.
    """
    event_dict["message"] = event_dict.pop("event", "")
    return event_dict


def setup_logging() -> None:
    """
    Configure structlog for structured JSON logging.
    Called once at application startup before any other initialization.
    """
    from app.core.config import get_settings

    settings = get_settings()

    # Shared processors applied to every log entry
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        add_service_context,
    ]

    if settings.is_development:
        # Human-readable output for development
        processors: list[Processor] = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # JSON output for production (Cloud Logging)
        processors = shared_processors + [
            rename_event_key,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging to route through structlog
    log_level = getattr(logging, settings.LOG_LEVEL, logging.DEBUG)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a named structured logger.
    Usage: logger = get_logger(__name__)
    """
    return structlog.get_logger(name)