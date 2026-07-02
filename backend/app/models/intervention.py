"""
SPARK — Intervention Domain Models
Interventions are SPARK's adaptive responses to task risk.
Stored in /tasks/{taskId}/interventions/{interventionId}.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentResponseDetail(BaseModel):
    nextAction: str
    rationale: str
    estimatedTimeToComplete: int  # minutes


class Intervention(BaseModel):
    """
    A single intervention event.
    Stored in /tasks/{taskId}/interventions/{interventionId}.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    taskId: str
    userId: str
    level: int = Field(ge=0, le=5)
    type: str    # suggestion | momentum | collaboration | critical | recovery
    trigger: str # risk_threshold | ponr_approaching | stalled | bankrupt | manual
    message: str
    actionRequired: Optional[str] = Field(default=None)
    agentResponse: Optional[AgentResponseDetail] = Field(default=None)
    outcome: Optional[str] = Field(default=None)  # accepted | dismissed | completed | ignored
    effectivenessScore: Optional[float] = Field(default=None, ge=0, le=10)
    createdAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    resolvedAt: Optional[str] = Field(default=None)

    def to_firestore(self) -> dict:
        return self.model_dump()


class RespondToInterventionRequest(BaseModel):
    """Validated request for responding to an intervention."""

    outcome: str = Field(description="accepted | dismissed | completed | ignored")


class Reflection(BaseModel):
    """
    Post-task reflection stored in /users/{userId}/reflections/{reflectionId}.
    Created by the Reflection Agent after task completion.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    userId: str
    taskId: str
    taskTitle: str
    completionStatus: str  # on_time | late | incomplete
    deadlineMet: bool
    daysLate: Optional[float] = Field(default=None)
    analysis: dict = Field(default_factory=dict)
    genomeUpdates: list[dict] = Field(default_factory=list)
    summary: str = Field(default="")
    insights: list[str] = Field(default_factory=list)
    createdAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_firestore(self) -> dict:
        return self.model_dump()