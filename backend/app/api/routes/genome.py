"""
SPARK — Genome Routes
Full genome profile and AI-generated insights.
"""

from typing import Any

from fastapi import APIRouter

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response
from app.services.genome_service import GenomeService
from app.services.genome_insights_service import GenomeInsightsService

router = APIRouter()
logger = get_logger(__name__)

_genome_service = GenomeService()
_insights_service = GenomeInsightsService()


@router.get("/genome", summary="Get user Completion Genome")
async def get_genome(user: CurrentUser) -> dict[str, Any]:
    """Returns the complete Completion Genome data."""
    genome = _genome_service.get_genome(user.uid)
    return success_response(data=genome.model_dump())


@router.get("/genome/profile", summary="Get genome profile with health score")
async def get_genome_profile(user: CurrentUser) -> dict[str, Any]:
    """Returns the structured genome profile for the dashboard."""
    full_insights = _insights_service.get_full_insights(user.uid)
    return success_response(data=full_insights["profile"])


@router.get("/genome/insights", summary="Get behavioral insights")
async def get_genome_insights(user: CurrentUser) -> dict[str, Any]:
    """Returns AI-generated behavioral insights from the genome."""
    full_insights = _insights_service.get_full_insights(user.uid)
    return success_response(
        data={
            "insights": full_insights["insights"],
            "generated_at": full_insights["generated_at"],
        }
    )


@router.get("/genome/full", summary="Get complete genome intelligence package")
async def get_genome_full(user: CurrentUser) -> dict[str, Any]:
    """
    Returns the complete genome intelligence package:
    - Profile with health score
    - All behavioral insights
    - Productivity heatmap data
    - Estimation accuracy data
    - Completion statistics
    - Intervention effectiveness
    """
    full_insights = _insights_service.get_full_insights(user.uid)
    return success_response(data=full_insights)


@router.get("/genome/productivity", summary="Get productivity pattern data")
async def get_productivity_data(user: CurrentUser) -> dict[str, Any]:
    """Returns hourly productivity data for the heatmap visualization."""
    full_insights = _insights_service.get_full_insights(user.uid)
    return success_response(data=full_insights["productivity_data"])


@router.get("/genome/estimation", summary="Get estimation accuracy data")
async def get_estimation_data(user: CurrentUser) -> dict[str, Any]:
    """Returns estimation accuracy and complexity calibration data."""
    full_insights = _insights_service.get_full_insights(user.uid)
    return success_response(data=full_insights["estimation_data"])