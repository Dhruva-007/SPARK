"""
SPARK — Milestone Domain Models
Milestones are the atomic units of task execution.
Stored as sub-collection: /tasks/{taskId}/milestones/{milestoneId}
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Milestone(BaseModel):
    """
    A single milestone within a task.
    Stored in Firestore /tasks/{taskId}/milestones/{milestoneId}.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    taskId: str
    title: str
    description: str = Field(default="")
    order: int = Field(ge=1)
    estimatedMinutes: int = Field(ge=5, le=480)
    actualMinutes: Optional[int] = Field(default=None)
    status: str = Field(default="pending")  # pending | in_progress | completed
    isNextAction: bool = Field(default=False)
    completedAt: Optional[str] = Field(default=None)
    createdAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_firestore(self) -> dict:
        return self.model_dump()


class CreateMilestoneRequest(BaseModel):
    """Validated API request for creating a milestone manually."""

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    order: int = Field(ge=1)
    estimatedMinutes: int = Field(ge=5, le=480)


class UpdateMilestoneRequest(BaseModel):
    """Validated API request for updating a milestone."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    estimatedMinutes: Optional[int] = Field(default=None, ge=5, le=480)
    status: Optional[str] = None
    isNextAction: Optional[bool] = None