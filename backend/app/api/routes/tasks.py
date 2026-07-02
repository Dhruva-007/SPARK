"""
SPARK — Task Routes
Full CRUD wired to TaskService.
create_task is async because it triggers the PlannerAgent.
"""

from typing import Any, Optional

from fastapi import APIRouter, Body, Query

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response
from app.models.task import CreateTaskRequest, UpdateTaskRequest, UpdateProgressRequest
from app.services.task_service import TaskService

router = APIRouter()
logger = get_logger(__name__)

_task_service = TaskService()


@router.get("/tasks", summary="List all tasks")
async def list_tasks(
    user: CurrentUser,
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
) -> dict[str, Any]:
    tasks = _task_service.list_tasks(user.uid, status=status, limit=limit)
    return success_response(
        data={"tasks": [t.model_dump() for t in tasks], "total": len(tasks)}
    )


@router.post("/tasks", summary="Create a new task", status_code=201)
async def create_task(
    user: CurrentUser,
    request: CreateTaskRequest = Body(...),
) -> dict[str, Any]:
    """
    Creates a task and immediately triggers the PlannerAgent
    to generate AI-powered milestones.
    """
    task = await _task_service.create_task(user.uid, request)
    return success_response(data=task.model_dump())


@router.get("/tasks/{task_id}", summary="Get task detail")
async def get_task(task_id: str, user: CurrentUser) -> dict[str, Any]:
    task = _task_service.get_task(task_id, user.uid)
    return success_response(data=task.model_dump())


@router.put("/tasks/{task_id}", summary="Update task")
async def update_task(
    task_id: str,
    user: CurrentUser,
    request: UpdateTaskRequest = Body(...),
) -> dict[str, Any]:
    task = _task_service.update_task(task_id, user.uid, request)
    return success_response(data=task.model_dump())


@router.delete("/tasks/{task_id}", summary="Delete task", status_code=204)
async def delete_task(task_id: str, user: CurrentUser) -> None:
    _task_service.delete_task(task_id, user.uid)


@router.post("/tasks/{task_id}/progress", summary="Update task progress")
async def update_progress(
    task_id: str,
    user: CurrentUser,
    request: UpdateProgressRequest = Body(...),
) -> dict[str, Any]:
    task = _task_service.update_progress(task_id, user.uid, request)
    return success_response(data=task.model_dump())


@router.post("/tasks/{task_id}/complete", summary="Mark task complete")
async def complete_task(task_id: str, user: CurrentUser) -> dict[str, Any]:
    task = await _task_service.complete_task(task_id, user.uid)
    return success_response(data=task.model_dump())


@router.post("/tasks/{task_id}/activate", summary="Run activation agent")
async def activate_task(task_id: str, user: CurrentUser) -> dict[str, Any]:
    """Manually triggers the ActivationAgent for a task."""
    from app.agents.orchestrator import AgentOrchestrator
    orchestrator = AgentOrchestrator()
    result = await orchestrator.run_activation_flow(user.uid, task_id)
    return success_response(data=result)


@router.get(
    "/tasks/{task_id}/next-action",
    summary="Get next best action for a task",
)
async def get_next_action(task_id: str, user: CurrentUser) -> dict[str, Any]:
    """Runs the MomentumAgent to get the next best action."""
    from app.agents.orchestrator import AgentOrchestrator
    orchestrator = AgentOrchestrator()
    result = await orchestrator.run_momentum_check(user.uid, task_id)
    return success_response(data=result)