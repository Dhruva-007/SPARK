"""
SPARK — Intervention Routes
Adaptive intervention management and chat.
"""

from typing import Any

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response

router = APIRouter()
logger = get_logger(__name__)


@router.get("/interventions", summary="List all interventions")
async def list_interventions(user: CurrentUser) -> dict[str, Any]:
    logger.info("List interventions stub", uid=user.uid)
    return success_response(data={"interventions": [], "total": 0})


@router.get(
    "/tasks/{task_id}/interventions",
    summary="List task interventions",
)
async def list_task_interventions(
    task_id: str, user: CurrentUser
) -> dict[str, Any]:
    logger.info("List task interventions stub", uid=user.uid, task_id=task_id)
    return success_response(data={"interventions": [], "task_id": task_id})


@router.post(
    "/interventions/{intervention_id}/respond",
    summary="Accept or dismiss intervention",
)
async def respond_to_intervention(
    intervention_id: str, user: CurrentUser
) -> dict[str, Any]:
    logger.info(
        "Respond to intervention stub",
        uid=user.uid,
        intervention_id=intervention_id,
    )
    return success_response(data={"intervention_id": intervention_id})


@router.post("/interventions/chat", summary="Chat with Intervention Agent")
async def intervention_chat(user: CurrentUser) -> dict[str, Any]:
    logger.info("Intervention chat stub", uid=user.uid)
    return success_response(
        data={"message": "Intervention agent coming in Phase 15"}
    )