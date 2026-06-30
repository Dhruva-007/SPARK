"""
SPARK — Health Check Routes
Liveness and readiness probes with real dependency checks.
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

_startup_time = time.time()
_VERSION = "1.0.0"


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: str
    uptime_seconds: float


class ReadinessResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: str
    uptime_seconds: float
    checks: dict[str, str]


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness Probe",
    tags=["Health"],
)
async def health_check() -> HealthResponse:
    """Liveness probe — confirms the process is running."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=round(time.time() - _startup_time, 2),
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Readiness Probe",
    tags=["Health"],
)
async def readiness_check() -> ReadinessResponse:
    """
    Readiness probe — checks all critical dependencies are reachable.
    """
    settings = get_settings()
    checks: dict[str, str] = {"api": "ok", "config": "ok"}

    # Firebase check
    try:
        from app.core.firebase import is_firebase_initialized
        checks["firebase"] = "ok" if is_firebase_initialized() else "not_initialized"
    except Exception as exc:
        checks["firebase"] = f"error: {str(exc)[:40]}"

    # Firestore check
    try:
        from app.core.firebase import get_firestore, is_firestore_available
        if is_firestore_available():
            db = get_firestore()
            db.collection("_health").document("probe").get()
            checks["firestore"] = "ok"
        else:
            checks["firestore"] = "not_initialized"
    except Exception as exc:
        logger.warning("Firestore health probe failed", error=str(exc))
        checks["firestore"] = "unreachable"

    # Vertex AI check
    try:
        from app.ai.vertex_client import is_vertex_ai_initialized
        checks["vertex_ai"] = "ok" if is_vertex_ai_initialized() else "not_initialized"
    except Exception as exc:
        checks["vertex_ai"] = f"error: {str(exc)[:40]}"

    all_ok = all(v == "ok" for v in checks.values())
    overall = "ok" if all_ok else "degraded"

    if overall != "ok":
        logger.warning("Readiness check degraded", checks=checks)

    return ReadinessResponse(
        status=overall,
        version=_VERSION,
        environment=settings.APP_ENV,
        timestamp=datetime.now(timezone.utc).isoformat(),
        uptime_seconds=round(time.time() - _startup_time, 2),
        checks=checks,
    )