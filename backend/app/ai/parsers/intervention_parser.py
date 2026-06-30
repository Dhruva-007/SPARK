"""
SPARK — Intervention Parser
Pydantic models for validating Intervention and Risk Agent responses.
"""

from typing import Literal
from pydantic import BaseModel, Field


class RiskAssessmentResponse(BaseModel):
    """Risk Prediction Agent output."""

    failure_probability: float = Field(
        description="Probability of failing to complete before deadline (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    primary_risk_factor: str = Field(
        description="Single most important risk factor"
    )
    ponr_timestamp: str | None = Field(
        description="ISO timestamp of Point of No Return, null if PONR already passed",
        default=None,
    )
    recommended_intervention_level: int = Field(
        description="Recommended intervention level (0-5)",
        ge=0,
        le=5,
    )
    immediate_action: str = Field(
        description="One specific action that would most reduce risk right now"
    )


class InterventionResponse(BaseModel):
    """Intervention Agent output for a specific intervention level."""

    message: str = Field(
        description="The intervention message to show the user"
    )
    next_action: str = Field(
        description="Specific next action required"
    )
    estimated_minutes: int = Field(
        description="Estimated time for the next action in minutes",
        ge=5,
        le=180,
    )
    rationale: str = Field(
        description="One sentence explaining the intervention choice"
    )


class RecoveryPlanResponse(BaseModel):
    """Recovery Agent output for damage minimization."""

    extension_email_subject: str = Field(
        description="Email subject line for extension request"
    )
    extension_email_body: str = Field(
        description="Full email body, ready to send"
    )
    partial_deliverable: str = Field(
        description="What can realistically be delivered by the deadline"
    )
    revised_deadline: str = Field(
        description="Proposed new deadline (ISO date)"
    )
    deprioritize_tasks: list[str] = Field(
        description="Task titles that should be deprioritized for recovery",
        default_factory=list,
    )
    next_two_hours: list[str] = Field(
        description="Specific actions for the next 2 hours",
        min_length=1,
        max_length=6,
    )


class BankruptcyAssessmentResponse(BaseModel):
    """Bankruptcy Engine assessment output."""

    bankruptcy_needed: bool = Field(
        description="Whether task bankruptcy should be declared"
    )
    prioritize_task_titles: list[str] = Field(
        description="Task titles to keep and focus on",
        default_factory=list,
    )
    sacrifice_task_titles: list[str] = Field(
        description="Task titles to defer or drop",
        default_factory=list,
    )
    prioritization_rationale: str = Field(
        description="Explanation of the prioritization decision"
    )
    focus_task: str = Field(
        description="The single most important task to focus on immediately"
    )
    workload_reduction: str = Field(
        description="Overall recommendation for reducing workload"
    )


class ReflectionResponse(BaseModel):
    """Reflection Agent output for genome updates."""

    what_worked: list[str] = Field(
        description="2-3 specific things that contributed to success",
        min_length=1,
        max_length=3,
    )
    what_caused_delays: list[str] = Field(
        description="2-3 specific causes of delays or failures",
        min_length=1,
        max_length=3,
    )
    effective_interventions: list[str] = Field(
        description="Interventions that helped and why",
        default_factory=list,
    )
    genome_updates: dict = Field(
        description="Specific genome parameter updates with new values"
    )
    behavioral_summary: str = Field(
        description="2-sentence behavioral summary for the user"
    )