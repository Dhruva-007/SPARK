"""
SPARK — Application Lifecycle Events
Manages startup and shutdown sequences using FastAPI lifespan.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.core.logging import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI lifespan context manager."""
    logger.info("SPARK backend starting up...")

    try:
        await _startup()
        logger.info("SPARK backend startup complete — ready to serve requests")
    except Exception as exc:
        logger.error("SPARK backend startup failed", error=str(exc))
        raise

    yield

    logger.info("SPARK backend shutting down...")
    await _shutdown()
    logger.info("SPARK backend shutdown complete")


async def _startup() -> None:
    """
    Execute all startup tasks in dependency order.

    Order:
    1. Validate configuration
    2. Initialize Firebase Admin SDK + Firestore
    3. Initialize Vertex AI SDK
    4. Register all agents
    """
    # ── Step 1: Configuration ──────────────────────────────
    logger.info("Startup: validating configuration")
    from app.core.config import get_settings
    settings = get_settings()
    logger.info(
        "Configuration validated",
        env=settings.APP_ENV,
        project=settings.GOOGLE_CLOUD_PROJECT,
        firebase_project=settings.FIREBASE_PROJECT_ID,
        model=settings.VERTEX_AI_MODEL,
    )

    # ── Step 2: Firebase + Firestore ───────────────────────
    logger.info("Startup: initializing Firebase")
    from app.core.firebase import initialize_firebase, is_firebase_initialized
    initialize_firebase()

    if is_firebase_initialized():
        logger.info("Firebase ready")
    else:
        logger.warning(
            "Firebase not initialized — auth and Firestore unavailable",
            hint="Provide FIREBASE_PROJECT_ID and service account credentials",
        )

    # ── Step 3: Vertex AI ──────────────────────────────────
    logger.info("Startup: initializing Vertex AI")
    from app.ai.vertex_client import initialize_vertex_ai, is_vertex_ai_initialized
    initialize_vertex_ai()

    if is_vertex_ai_initialized():
        logger.info("Vertex AI ready", model=settings.VERTEX_AI_MODEL)
    else:
        logger.warning(
            "Vertex AI not initialized — AI features unavailable",
            hint="Provide GOOGLE_CLOUD_PROJECT and credentials",
        )

    # ── Step 4: Register Agents ────────────────────────────
    logger.info("Startup: registering agents")
    import app.agents  # noqa: F401 — triggers __init__.py which registers all agents
    from app.agents.registry import list_agents
    registered = list_agents()
    logger.info(
        "Agents registered",
        agents=registered,
        count=len(registered),
    )

    logger.info("All startup tasks complete")


async def _shutdown() -> None:
    """Cleanup on shutdown."""
    logger.info("Shutdown complete")