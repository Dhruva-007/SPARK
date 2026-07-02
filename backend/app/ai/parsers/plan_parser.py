"""
SPARK — Plan Parser
Pydantic models for validating Planner Agent responses.
Relaxed validation to handle Gemini output variations.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class MilestonePlan(BaseModel):
    """A single milestone in an execution plan."""

    title: str = Field(description="Specific, actionable milestone title")
    description: str = Field(default="", description="What exactly needs to be done")
    order: int = Field(default=1, description="Sequence number starting from 1")
    estimated_minutes: int = Field(
        default=60,
        description="Realistic time estimate in minutes",
    )
    is_first_action: bool = Field(
        default=False,
        description="True only for the very first milestone",
    )

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: str) -> str:
        return v.strip()

    @field_validator("estimated_minutes", mode="before")
    @classmethod
    def clamp_estimate(cls, v: object) -> int:
        try:
            val = int(v)  # type: ignore[arg-type]
            return max(5, min(480, val))
        except (TypeError, ValueError):
            return 60

    @field_validator("order", mode="before")
    @classmethod
    def ensure_positive_order(cls, v: object) -> int:
        try:
            return max(1, int(v))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 1


class ExecutionPlan(BaseModel):
    """Complete execution plan for a task."""

    milestones: list[MilestonePlan] = Field(
        default_factory=list,
        description="Ordered list of milestones",
    )
    total_estimated_hours: float = Field(
        default=1.0,
        description="Sum of all milestone estimates in hours",
    )
    first_action: str = Field(
        default="Open a new document and write the task title",
        description="The single smallest action to take immediately",
    )
    implicit_requirements: list[str] = Field(
        default_factory=list,
        description="Requirements not explicitly stated but implied",
    )
    confidence: float = Field(
        default=0.8,
        description="Confidence in this plan (0.0 to 1.0)",
    )

    @field_validator("total_estimated_hours", mode="before")
    @classmethod
    def parse_hours(cls, v: object) -> float:
        try:
            return round(float(v), 1)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 1.0

    @field_validator("confidence", mode="before")
    @classmethod
    def clamp_confidence(cls, v: object) -> float:
        try:
            return max(0.0, min(1.0, float(v)))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 0.8

    @model_validator(mode="after")
    def ensure_milestones_exist(self) -> "ExecutionPlan":
        """
        If Gemini returns fewer than 2 milestones,
        generate sensible defaults rather than failing.
        """
        if len(self.milestones) < 2:
            self.milestones = [
                MilestonePlan(
                    title="Start and outline the task",
                    description="Create an initial structure and plan",
                    order=1,
                    estimated_minutes=30,
                    is_first_action=True,
                ),
                MilestonePlan(
                    title="Complete the main work",
                    description="Execute the primary task requirements",
                    order=2,
                    estimated_minutes=int(self.total_estimated_hours * 60 - 30),
                    is_first_action=False,
                ),
            ]

        # Ensure first milestone is marked as first action
        if self.milestones and not any(m.is_first_action for m in self.milestones):
            self.milestones[0].is_first_action = True

        # Re-number orders sequentially
        for i, milestone in enumerate(self.milestones):
            milestone.order = i + 1

        return self