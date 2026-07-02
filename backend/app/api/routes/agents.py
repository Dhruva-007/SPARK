"""
SPARK — Agent Routes
Agent status, manual triggers, and memory inspection.
"""

from typing import Any

from fastapi import APIRouter, Body

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response

router = APIRouter()
logger = get_logger(__name__)


@router.post("/agents/run", summary="Manually trigger a specific agent")
async def run_agent(
    user: CurrentUser,
    body: dict = Body(...),
) -> dict[str, Any]:
    from app.agents.orchestrator import AgentOrchestrator

    agent_name = body.get("agent_name")
    task_id = body.get("task_id")

    if not agent_name:
        return success_response(data={"error": "agent_name is required"})

    orchestrator = AgentOrchestrator()
    context = await orchestrator.build_context(
        user_id=user.uid,
        task_id=task_id,
    )
    result = await orchestrator.run_agent(agent_name, context)

    return success_response(
        data={
            "agent": agent_name,
            "success": result.success,
            "data": result.data,
            "error": result.error,
            "duration_ms": result.execution_time_ms,
        }
    )


@router.get("/agents/status", summary="List registered agents")
async def get_agent_status(user: CurrentUser) -> dict[str, Any]:
    from app.agents.registry import list_agents
    registered = list_agents()
    return success_response(
        data={
            "registered_agents": registered,
            "total": len(registered),
        }
    )


@router.get("/agents/memory", summary="Inspect current memory state")
async def get_memory_state(user: CurrentUser) -> dict[str, Any]:
    """
    Returns the current memory state for the authenticated user.
    Useful for debugging and the Genome page in the frontend.
    """
    try:
        from app.memory.short_term import ShortTermMemory
        from app.memory.long_term import LongTermMemory

        stm = ShortTermMemory()
        ltm = LongTermMemory()

        session_summary = stm.get_session_summary(user.uid)
        behavioral_summary = ltm.get_behavioral_summary(user.uid)
        stm_context = stm.compress_for_prompt(user.uid)
        ltm_context = ltm.compress_for_prompt(user.uid)

        return success_response(
            data={
                "short_term": {
                    "session_summary": session_summary,
                    "compressed_context": stm_context,
                },
                "long_term": {
                    "behavioral_summary": behavioral_summary,
                    "compressed_context": ltm_context,
                },
            }
        )
    except Exception as exc:
        logger.error("Memory state retrieval failed", error=str(exc))
        return success_response(
            data={"error": str(exc)}
        )


@router.post("/agents/memory/record", summary="Record a session observation")
async def record_observation(
    user: CurrentUser,
    body: dict = Body(...),
) -> dict[str, Any]:
    """
    Records a manual observation to short-term memory.
    Body: { "type": str, "data": dict, "task_id": str (optional) }
    """
    try:
        from app.memory.short_term import ShortTermMemory
        stm = ShortTermMemory()
        stm.record(
            user_id=user.uid,
            observation_type=body.get("type", "manual"),
            data=body.get("data", {}),
            task_id=body.get("task_id"),
        )
        return success_response(data={"recorded": True})
    except Exception as exc:
        return success_response(data={"recorded": False, "error": str(exc)})


@router.post("/agents/test-gemini", summary="Test Gemini connectivity")
async def test_gemini(user: CurrentUser) -> dict[str, Any]:
    from app.core.config import get_settings
    settings = get_settings()

    if settings.is_production:
        return success_response(
            data={"message": "Test endpoint disabled in production"}
        )

    try:
        from app.ai.gemini_client import get_gemini_client
        client = get_gemini_client()
        response = await client.generate(
            prompt='Reply with exactly this JSON: {"status": "connected", "model": "gemini-2.5-flash"}',
            agent_role="default",
            temperature=0,
        )
        return success_response(
            data={
                "status": "connected",
                "model": settings.VERTEX_AI_MODEL,
                "response": response,
            }
        )
    except Exception as exc:
        return success_response(
            data={"status": "failed", "error": str(exc)}
        )