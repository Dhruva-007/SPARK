"""
SPARK — CMS Routes
Wired to real CMSService.
"""

from typing import Any

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response
from app.services.cms_service import CMSService

router = APIRouter()
logger = get_logger(__name__)

_cms_service = CMSService()


@router.get("/tasks/{task_id}/cms", summary="Get current CMS for a task")
async def get_cms(task_id: str, user: CurrentUser) -> dict[str, Any]:
    result = _cms_service.recalculate_for_task(task_id, user.uid)
    return success_response(data=result.model_dump())


@router.post(
    "/tasks/{task_id}/cms/recalculate",
    summary="Force CMS recalculation",
)
async def recalculate_cms(task_id: str, user: CurrentUser) -> dict[str, Any]:
    result = _cms_service.recalculate_for_task(task_id, user.uid)
    return success_response(data=result.model_dump())