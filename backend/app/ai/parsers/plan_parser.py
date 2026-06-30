"""
SPARK — Plan Parser
Pydantic models for validating Planner Agent responses.
"""

from pydantic import BaseModel, Field, field_validator


class MilestonePlan(BaseModel):
    """A single milestone in an execution plan."""

    title: str = Field(description="Specific, actionable milestone title")
    description: str = Field(description="What exactly needs to be done")
    order: int = Field(description="Sequence number starting from 1")
    estimated_minutes: int = Field(
        description="Realistic time estimate in minutes",
        ge=5,
        le=480,
    )
    is_first_action: bool = Field(
        default=False,
        description="True only for the very first milestone",
    )

    @field_validator("title")
    @classmethod
    def title_must_be_clean(cls, v: str) -> str:
        return v.strip()

    @field_validator("estimated_minutes")
    @classmethod
    def clamp_estimate(cls, v: int) -> int:
        return max(5, min(480, v))


class ExecutionPlan(BaseModel):
    """Complete execution plan for a task."""

    milestones: list[MilestonePlan] = Field(
        description="Ordered list of milestones",
        min_length=2,
        max_length=12,
    )
    total_estimated_hours: float = Field(
        description="Sum of all milestone estimates in hours"
    )
    first_action: str = Field(
        description="The single smallest action to take immediately (under 5 minutes)"
    )
    implicit_requirements: list[str] = Field(
        default_factory=list,
        description="Requirements not explicitly stated but implied by the task",
    )
    confidence: float = Field(
        description="Confidence in this plan (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )

    @field_validator("total_estimated_hours", mode="before")
    @classmethod
    def round_total(cls, v: float) -> float:
        return round(float(v), 1)