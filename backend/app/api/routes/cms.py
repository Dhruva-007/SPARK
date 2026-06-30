"""
SPARK — Completion Momentum Score Routes
CMS retrieval and recalculation endpoints.
"""

from typing import Any

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response

router = APIRouter()
logger = get_logger(__name__)


@router.get("/tasks/{task_id}/cms", summary="Get current CMS for a task")
async def get_cms(task_id: str, user: CurrentUser) -> dict[str, Any]:
    logger.info("Get CMS stub", uid=user.uid, task_id=task_id)
    return success_response(
        data={
            "task_id": task_id,
            "score": 0,
            "momentum": 0,
            "failure_risk": 0,
            "completion_probability": 0,
            "trend": "stable",
        }
    )


@router.post(
    "/tasks/{task_id}/cms/recalculate",
    summary="Force CMS recalculation",
)
async def recalculate_cms(task_id: str, user: CurrentUser) -> dict[str, Any]:
    logger.info("Recalculate CMS stub", uid=user.uid, task_id=task_id)
    return success_response(data={"message": "CMS service coming in Phase 12"})