"""
SPARK — Analytics Routes
Wired to real services with simulation support.
"""

from typing import Any
from datetime import datetime, timezone

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response
from app.services.analytics_service import AnalyticsService

router = APIRouter()
logger = get_logger(__name__)

_analytics_service = AnalyticsService()


@router.get("/analytics/completion-health", summary="Overall completion health score")
async def get_completion_health(user: CurrentUser) -> dict[str, Any]:
    health = _analytics_service.get_completion_health(user.uid)
    return success_response(data=health)


@router.get("/analytics/risk-matrix", summary="All tasks risk matrix")
async def get_risk_matrix(user: CurrentUser) -> dict[str, Any]:
    matrix = _analytics_service.get_risk_matrix(user.uid)
    return success_response(
        data={
            "tasks": matrix,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    )


@router.get("/analytics/history", summary="Historical completion data")
async def get_history(user: CurrentUser) -> dict[str, Any]:
    return success_response(data={"records": [], "period_days": 30})


@router.get("/analytics/simulation", summary="Run workload simulation")
async def get_simulation(user: CurrentUser) -> dict[str, Any]:
    """Runs the SimulationAgent and returns workload analysis."""
    from app.agents.orchestrator import AgentOrchestrator

    orchestrator = AgentOrchestrator()
    context = await orchestrator.build_context(user_id=user.uid)
    result = await orchestrator.run_agent("simulation_agent", context)

    if result.success:
        return success_response(data=result.data)
    else:
        return success_response(
            data={"error": result.error}
        )