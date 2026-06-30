"""
SPARK — Milestone Parser
Pydantic models for validating Momentum Agent responses.
"""

from typing import Literal
from pydantic import BaseModel, Field


class NextActionResponse(BaseModel):
    """The Momentum Agent's next best action recommendation."""

    action: str = Field(
        description="Single specific action starting with a verb"
    )
    estimated_minutes: int = Field(
        description="Estimated time to complete in minutes",
        ge=5,
        le=90,
    )
    rationale: str = Field(
        description="One sentence explaining why this action now"
    )
    milestone_id: str | None = Field(
        default=None,
        description="ID of the milestone this action advances",
    )


class CMSAdjustmentResponse(BaseModel):
    """Qualitative CMS adjustment from the Momentum Agent."""

    score_adjustment: float = Field(
        description="Adjustment to apply to mathematical baseline (-20 to +20)",
        ge=-20.0,
        le=20.0,
    )
    primary_factor: str = Field(
        description="Main factor driving this adjustment"
    )
    failure_risk: float = Field(
        description="Failure risk percentage (0-100)",
        ge=0.0,
        le=100.0,
    )
    trend: Literal["improving", "stable", "declining", "critical"] = Field(
        description="Current momentum trend direction"
    )