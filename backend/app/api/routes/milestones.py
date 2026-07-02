"""
SPARK — Milestone Routes
Wired to real TaskService.
"""

from typing import Any

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response
from app.services.task_service import TaskService

router = APIRouter()
logger = get_logger(__name__)

_task_service = TaskService()


@router.get("/tasks/{task_id}/milestones", summary="List task milestones")
async def list_milestones(task_id: str, user: CurrentUser) -> dict[str, Any]:
    milestones = _task_service.get_milestones(task_id, user.uid)
    return success_response(
        data={
            "milestones": [m.model_dump() for m in milestones],
            "task_id": task_id,
        }
    )


@router.post(
    "/tasks/{task_id}/milestones",
    summary="Create milestone",
    status_code=201,
)
async def create_milestone(task_id: str, user: CurrentUser) -> dict[str, Any]:
    return success_response(
        data={"message": "Manual milestone creation coming in Phase 8"}
    )


@router.put(
    "/tasks/{task_id}/milestones/{milestone_id}",
    summary="Update milestone",
)
async def update_milestone(
    task_id: str, milestone_id: str, user: CurrentUser
) -> dict[str, Any]:
    return success_response(data={"milestone_id": milestone_id})


@router.post(
    "/tasks/{task_id}/milestones/{milestone_id}/complete",
    summary="Complete milestone",
)
async def complete_milestone(
    task_id: str, milestone_id: str, user: CurrentUser
) -> dict[str, Any]:
    milestones = _task_service.complete_milestone(task_id, milestone_id, user.uid)
    return success_response(
        data={
            "milestones": [m.model_dump() for m in milestones],
            "task_id": task_id,
        }
    )