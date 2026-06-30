"""
SPARK — Webhook Routes
Internal endpoints called by Cloud Scheduler, Cloud Tasks, and Pub/Sub.
These are NOT user-facing endpoints. They are called by GCP services.

Security: In production, these endpoints are secured by verifying
the OIDC token from the Cloud Scheduler/Tasks service account.
In development, they can be called directly for testing.
"""

from typing import Any

from fastapi import APIRouter, Request

from app.core.logging import get_logger
from app.models.common import success_response

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/webhooks/cms-worker",
    summary="Triggered by Cloud Scheduler — recalculates CMS for all active tasks",
    include_in_schema=False,
)
async def cms_worker_webhook(request: Request) -> dict[str, Any]:
    logger.info("CMS worker webhook triggered")
    return success_response(data={"message": "CMS worker coming in Phase 12"})


@router.post(
    "/webhooks/ponr-worker",
    summary="Triggered by Cloud Scheduler — scans for PONR crossings",
    include_in_schema=False,
)
async def ponr_worker_webhook(request: Request) -> dict[str, Any]:
    logger.info("PONR worker webhook triggered")
    return success_response(data={"message": "PONR worker coming in Phase 13"})


@router.post(
    "/webhooks/task-activation",
    summary="Triggered by Cloud Tasks — runs activation agent for a task",
    include_in_schema=False,
)
async def task_activation_webhook(request: Request) -> dict[str, Any]:
    logger.info("Task activation webhook triggered")
    return success_response(data={"message": "Activation agent coming in Phase 8"})