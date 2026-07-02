"""
SPARK — Webhook Routes
Internal endpoints called by Cloud Scheduler and Cloud Tasks.
In development these can be called manually for testing.
"""

from typing import Any

from fastapi import APIRouter, Request

from app.core.logging import get_logger
from app.models.common import success_response

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/webhooks/cms-worker",
    summary="Recalculates CMS for all active tasks",
    include_in_schema=False,
)
async def cms_worker_webhook(request: Request) -> dict[str, Any]:
    """
    Triggered by Cloud Scheduler every 15 minutes.
    In development, can be called manually to test.
    """
    from app.workers.cms_worker import run_cms_worker

    # In production: extract user_id from Pub/Sub message
    # In development: use dev user
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass

    user_id = body.get("user_id", "dev-user-001")
    logger.info("CMS worker triggered", user_id=user_id)

    result = await run_cms_worker(user_id)
    return success_response(data=result)


@router.post(
    "/webhooks/ponr-worker",
    summary="Scans for PONR crossings",
    include_in_schema=False,
)
async def ponr_worker_webhook(request: Request) -> dict[str, Any]:
    """Triggered by Cloud Scheduler every 30 minutes."""
    from app.workers.ponr_worker import run_ponr_worker

    body = {}
    try:
        body = await request.json()
    except Exception:
        pass

    user_id = body.get("user_id", "dev-user-001")
    logger.info("PONR worker triggered", user_id=user_id)

    result = await run_ponr_worker(user_id)
    return success_response(data=result)


@router.post(
    "/webhooks/task-activation",
    summary="Runs activation agent for a task",
    include_in_schema=False,
)
async def task_activation_webhook(request: Request) -> dict[str, Any]:
    """Triggered by Cloud Tasks after task creation."""
    body = {}
    try:
        body = await request.json()
    except Exception:
        pass

    user_id = body.get("user_id", "dev-user-001")
    task_id = body.get("task_id")

    if not task_id:
        return success_response(data={"error": "task_id is required"})

    from app.agents.orchestrator import AgentOrchestrator
    orchestrator = AgentOrchestrator()
    result = await orchestrator.run_activation_flow(user_id, task_id)

    return success_response(data=result)