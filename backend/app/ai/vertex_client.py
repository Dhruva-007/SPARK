"""
SPARK — Vertex AI Client Initialization
Manages the Vertex AI SDK connection lifecycle.

The SDK uses Application Default Credentials (ADC) automatically
when running on Cloud Run. Locally, it uses the service account
file specified in GOOGLE_APPLICATION_CREDENTIALS.

Design decisions:
- Single initialization at startup via initialize_vertex_ai()
- Module-level state with availability flag
- Separate from GeminiClient — this handles SDK-level concerns
- GeminiClient handles model-level concerns
"""

import os
from typing import Optional

import vertexai
from vertexai.generative_models import GenerativeModel

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Module-level state
_initialized: bool = False
_project: Optional[str] = None
_location: Optional[str] = None


def initialize_vertex_ai() -> None:
    """
    Initialize the Vertex AI SDK.
    Called once during application startup in events.py.
    Safe to call multiple times — subsequent calls are no-ops.

    Initialization uses:
    1. GOOGLE_APPLICATION_CREDENTIALS env var (local dev)
    2. Application Default Credentials (Cloud Run — automatic)
    """
    global _initialized, _project, _location

    if _initialized:
        logger.debug("Vertex AI already initialized — skipping")
        return

    settings = get_settings()

    if not settings.GOOGLE_CLOUD_PROJECT:
        logger.warning(
            "GOOGLE_CLOUD_PROJECT not set — Vertex AI will not be available",
            hint="Set GOOGLE_CLOUD_PROJECT in .env to enable AI features",
        )
        return

    try:
        # Set credentials path if service account file exists
        credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        if credentials_path and os.path.exists(credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            logger.debug(
                "Using service account credentials",
                path=credentials_path,
            )

        vertexai.init(
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_REGION,
        )

        _initialized = True
        _project = settings.GOOGLE_CLOUD_PROJECT
        _location = settings.GOOGLE_CLOUD_REGION

        logger.info(
            "Vertex AI initialized",
            project=_project,
            location=_location,
            model=settings.VERTEX_AI_MODEL,
        )

    except Exception as exc:
        logger.error(
            "Vertex AI initialization failed",
            error=str(exc),
            hint="Verify GOOGLE_CLOUD_PROJECT and credentials are correct",
        )
        # Non-fatal — app starts with degraded AI functionality


def is_vertex_ai_initialized() -> bool:
    """Returns True if Vertex AI SDK has been successfully initialized."""
    return _initialized


def get_generative_model(model_name: str) -> GenerativeModel:
    """
    Returns a configured GenerativeModel instance.
    Raises ServiceUnavailableError if Vertex AI is not initialized.
    """
    if not _initialized:
        from app.core.exceptions import ServiceUnavailableError
        raise ServiceUnavailableError("Vertex AI")

    return GenerativeModel(model_name)


async def probe_vertex_ai(model_name: str) -> bool:
    """
    Lightweight probe to verify Vertex AI is reachable.
    Used by the health check endpoint.
    Returns True if successful, False otherwise.
    """
    if not _initialized:
        return False

    try:
        model = GenerativeModel(model_name)
        # Minimal generation to verify the model responds
        response = model.generate_content(
            "Reply with the single word: ok",
            generation_config={"max_output_tokens": 5, "temperature": 0},
        )
        return bool(response.text)
    except Exception as exc:
        logger.warning("Vertex AI probe failed", error=str(exc))
        return False