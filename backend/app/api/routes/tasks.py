"""
SPARK — Task Routes
Full CRUD and lifecycle management for tasks.
"""

from typing import Any

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response

router = APIRouter()
logger = get_logger(__name__)


@router.get("/tasks", summary="List all tasks")
async def list_tasks(user: CurrentUser) -> dict[str, Any]:
    logger.info("List tasks stub", uid=user.uid)
    return success_response(data={"tasks": [], "total": 0})


@router.post("/tasks", summary="Create a new task", status_code=201)
async def create_task(user: CurrentUser) -> dict[str, Any]:
    logger.info("Create task stub", uid=user.uid)
    return success_response(data={"message": "Task service coming in Phase 7"})


@router.get("/tasks/{task_id}", summary="Get task detail")
async def get_task(task_id: str, user: CurrentUser) -> dict[str, Any]:
    logger.info("Get task stub", uid=user.uid, task_id=task_id)
    return success_response(data={"task_id": task_id})


@router.put("/tasks/{task_id}", summary="Update task")
async def update_task(task_id: str, user: CurrentUser) -> dict[str, Any]:
    logger.info("Update task stub", uid=user.uid, task_id=task_id)
    return success_response(data={"task_id": task_id})


@router.delete("/tasks/{task_id}", summary="Delete task", status_code=204)
async def delete_task(task_id: str, user: CurrentUser) -> None:
    logger.info("Delete task stub", uid=user.uid, task_id=task_id)


@router.post("/tasks/{task_id}/progress", summary="Update task progress")
async def update_progress(task_id: str, user: CurrentUser) -> dict[str, Any]:
    logger.info("Update progress stub", uid=user.uid, task_id=task_id)
    return success_response(data={"task_id": task_id})


@router.post("/tasks/{task_id}/complete", summary="Mark task complete")
async def complete_task(task_id: str, user: CurrentUser) -> dict[str, Any]:
    logger.info("Complete task stub", uid=user.uid, task_id=task_id)
    return success_response(data={"task_id": task_id})


@router.post("/tasks/{task_id}/activate", summary="Trigger activation agent")
async def activate_task(task_id: str, user: CurrentUser) -> dict[str, Any]:
    logger.info("Activate task stub", uid=user.uid, task_id=task_id)
    return success_response(data={"task_id": task_id})