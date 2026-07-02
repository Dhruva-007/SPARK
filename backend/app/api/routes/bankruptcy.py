"""
SPARK — Task Bankruptcy Routes
Wired to real BankruptcyService.
"""

from typing import Any

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response

router = APIRouter()
logger = get_logger(__name__)


@router.get("/bankruptcy/assess", summary="Assess if task bankruptcy is needed")
async def assess_bankruptcy(user: CurrentUser) -> dict[str, Any]:
    """
    Runs the SimulationAgent and AI triage to assess workload.
    Does NOT declare bankruptcy — only provides the assessment.
    """
    from app.services.bankruptcy_service import BankruptcyService
    service = BankruptcyService()
    assessment = await service.assess_bankruptcy(user.uid)
    return success_response(data=assessment)


@router.post(
    "/bankruptcy/declare",
    summary="Declare task bankruptcy",
    status_code=201,
)
async def declare_bankruptcy(user: CurrentUser) -> dict[str, Any]:
    """
    Officially declares Task Bankruptcy.
    Sacrificed tasks are marked as bankrupt.
    """
    from app.services.bankruptcy_service import BankruptcyService
    service = BankruptcyService()
    result = await service.declare_bankruptcy(user.uid)
    return success_response(data=result)


@router.put(
    "/bankruptcy/{bankruptcy_id}/resolve",
    summary="Mark bankruptcy resolved",
)
async def resolve_bankruptcy(
    bankruptcy_id: str,
    user: CurrentUser,
) -> dict[str, Any]:
    """Marks a bankruptcy event as resolved."""
    from datetime import datetime, timezone

    try:
        from app.core.firebase import get_firestore
        db = get_firestore()
        db.collection("bankruptcies").document(bankruptcy_id).update({
            "resolved": True,
            "resolvedAt": datetime.now(timezone.utc).isoformat(),
        })
        return success_response(data={"resolved": True})
    except Exception as exc:
        logger.error("Could not resolve bankruptcy", error=str(exc))
        return success_response(data={"resolved": False, "error": str(exc)})