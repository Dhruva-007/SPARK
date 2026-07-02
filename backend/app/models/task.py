"""
SPARK — Task Domain Models
Internal Pydantic models for tasks and their sub-components.
Mirrors the Firestore schema defined in Phase 0 architecture exactly.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ── Enums as string literals ──────────────────────────────────

TaskStatus = str       # pending | active | in_progress | completed | failed | bankrupt
TaskPriority = str     # critical | high | medium | low
TaskCategory = str     # academic | work | personal
TaskComplexity = str   # low | medium | high
CMSTrend = str         # improving | stable | declining | critical


# ── Sub-models ────────────────────────────────────────────────

class TaskProgress(BaseModel):
    percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    lastUpdatedAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    milestonesCurrent: int = Field(default=0, ge=0)
    milestonesTotal: int = Field(default=0, ge=0)


class TaskCMS(BaseModel):
    score: float = Field(default=0.0, ge=0.0, le=100.0)
    momentum: float = Field(default=0.0, ge=0.0, le=100.0)
    failureRisk: float = Field(default=0.0, ge=0.0, le=100.0)
    completionProbability: float = Field(default=0.5, ge=0.0, le=1.0)
    lastCalculatedAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    trend: CMSTrend = Field(default="stable")


class TaskPONR(BaseModel):
    calculatedAt: Optional[str] = Field(default=None)
    ponrTime: Optional[str] = Field(default=None)
    ponrPassed: bool = Field(default=False)
    remainingWorkHours: float = Field(default=0.0, ge=0.0)
    remainingAvailableHours: float = Field(default=0.0, ge=0.0)


class TaskActivation(BaseModel):
    isActivated: bool = Field(default=False)
    googleDocId: Optional[str] = Field(default=None)
    googleDocUrl: Optional[str] = Field(default=None)
    checklistGenerated: bool = Field(default=False)
    outlineGenerated: bool = Field(default=False)
    activatedAt: Optional[str] = Field(default=None)


# ── Main Task model ───────────────────────────────────────────

class Task(BaseModel):
    """
    Complete task as stored in Firestore /tasks/{taskId}.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    userId: str
    title: str
    description: str = Field(default="")
    category: TaskCategory = Field(default="personal")
    priority: TaskPriority = Field(default="medium")
    status: TaskStatus = Field(default="pending")

    deadline: str
    estimatedHours: float = Field(default=1.0, gt=0)
    actualHoursSpent: float = Field(default=0.0, ge=0)

    complexity: TaskComplexity = Field(default="medium")

    progress: TaskProgress = Field(default_factory=TaskProgress)
    cms: TaskCMS = Field(default_factory=TaskCMS)
    ponr: TaskPONR = Field(default_factory=TaskPONR)
    activation: TaskActivation = Field(default_factory=TaskActivation)

    tags: list[str] = Field(default_factory=list)
    googleCalendarEventId: Optional[str] = Field(default=None)
    googleTaskId: Optional[str] = Field(default=None)

    createdAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updatedAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completedAt: Optional[str] = Field(default=None)

    @classmethod
    def create_new(
        cls,
        user_id: str,
        title: str,
        description: str,
        category: str,
        priority: str,
        deadline: str,
        estimated_hours: float,
        complexity: str,
        tags: Optional[list[str]] = None,
    ) -> "Task":
        """Factory method for creating a new task."""
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            userId=user_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            status="pending",
            deadline=deadline,
            estimatedHours=estimated_hours,
            complexity=complexity,
            tags=tags or [],
            createdAt=now,
            updatedAt=now,
        )

    def to_firestore(self) -> dict:
        """Serializes to Firestore-compatible dict."""
        return self.model_dump()


# ── Request models ────────────────────────────────────────────

class CreateTaskRequest(BaseModel):
    """Validated API request for creating a task."""

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    category: str = Field(default="personal")
    priority: str = Field(default="medium")
    deadline: str = Field(description="ISO datetime string")
    estimatedHours: float = Field(gt=0, le=1000)
    complexity: str = Field(default="medium")
    tags: list[str] = Field(default_factory=list)


class UpdateTaskRequest(BaseModel):
    """Validated API request for updating a task."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[str] = None
    deadline: Optional[str] = None
    estimatedHours: Optional[float] = Field(default=None, gt=0)
    tags: Optional[list[str]] = None


class UpdateProgressRequest(BaseModel):
    """Validated request for updating task progress percentage."""

    percentage: float = Field(ge=0.0, le=100.0)