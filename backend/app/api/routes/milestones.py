"""
SPARK — Milestone Routes
Milestone management within tasks.
"""

from typing import Any

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response

router = APIRouter()
logger = get_logger(__name__)


@router.get("/tasks/{task_id}/milestones", summary="List task milestones")
async def list_milestones(task_id: str, user: CurrentUser) -> dict[str, Any]:
    logger.info("List milestones stub", uid=user.uid, task_id=task_id)
    return success_response(data={"milestones": [], "task_id": task_id})


@router.post(
    "/tasks/{task_id}/milestones",
    summary="Create milestone",
    status_code=201,
)
async def create_milestone(task_id: str, user: CurrentUser) -> dict[str, Any]:
    logger.info("Create milestone stub", uid=user.uid, task_id=task_id)
    return success_response(data={"message": "Milestone service coming in Phase 7"})


@router.put(
    "/tasks/{task_id}/milestones/{milestone_id}",
    summary="Update milestone",
)
async def update_milestone(
    task_id: str, milestone_id: str, user: CurrentUser
) -> dict[str, Any]:
    logger.info(
        "Update milestone stub",
        uid=user.uid,
        task_id=task_id,
        milestone_id=milestone_id,
    )
    return success_response(data={"milestone_id": milestone_id})


@router.post(
    "/tasks/{task_id}/milestones/{milestone_id}/complete",
    summary="Complete milestone",
)
async def complete_milestone(
    task_id: str, milestone_id: str, user: CurrentUser
) -> dict[str, Any]:
    logger.info(
        "Complete milestone stub",
        uid=user.uid,
        task_id=task_id,
        milestone_id=milestone_id,
    )
    return success_response(data={"milestone_id": milestone_id})