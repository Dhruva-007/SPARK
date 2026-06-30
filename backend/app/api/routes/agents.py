"""
SPARK — Agent Management Routes
Manual agent triggering and Gemini connectivity testing.
"""

from typing import Any

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response

router = APIRouter()
logger = get_logger(__name__)


@router.post("/agents/run", summary="Manually trigger a specific agent")
async def run_agent(user: CurrentUser) -> dict[str, Any]:
    logger.info("Run agent stub", uid=user.uid)
    return success_response(data={"message": "Agent framework coming in Phase 8"})


@router.get("/agents/status", summary="Get agent run history")
async def get_agent_status(user: CurrentUser) -> dict[str, Any]:
    logger.info("Get agent status stub", uid=user.uid)
    return success_response(data={"runs": [], "total": 0})


@router.post(
    "/agents/test-gemini",
    summary="Test Gemini 2.5 Flash connectivity",
    tags=["Agents"],
)
async def test_gemini(user: CurrentUser) -> dict[str, Any]:
    """
    Sends a minimal prompt to Gemini and returns the response.
    Used to verify Vertex AI connectivity end-to-end.
    Only available in non-production environments.
    """
    from app.core.config import get_settings
    settings = get_settings()

    if settings.is_production:
        return success_response(
            data={"message": "Test endpoint disabled in production"}
        )

    logger.info("Testing Gemini connectivity", uid=user.uid)

    try:
        from app.ai.gemini_client import get_gemini_client

        client = get_gemini_client()
        response = await client.generate(
            prompt=(
                "You are a component of SPARK, an AI productivity system. "
                "Respond with exactly this JSON: "
                '{"status": "connected", "model": "gemini-2.5-flash", "message": "SPARK AI is operational"}'
            ),
            agent_role="default",
            temperature=0,
        )

        logger.info("Gemini test successful", uid=user.uid)

        return success_response(
            data={
                "gemini_response": response,
                "model": settings.VERTEX_AI_MODEL,
                "project": settings.GOOGLE_CLOUD_PROJECT,
                "status": "connected",
            }
        )

    except Exception as exc:
        logger.error("Gemini test failed", uid=user.uid, error=str(exc))
        return success_response(
            data={
                "status": "failed",
                "error": str(exc),
                "hint": "Verify GOOGLE_CLOUD_PROJECT and credentials in .env",
            }
        )