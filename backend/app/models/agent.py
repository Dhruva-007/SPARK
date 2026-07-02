"""
SPARK — Agent Domain Models
Data transfer objects for agent inputs and outputs.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class CalendarEvent(BaseModel):
    """Represents a calendar event for context."""
    title: str
    start: str
    end: str
    is_busy: bool = True


class AgentContext(BaseModel):
    """
    Shared context passed to every agent.
    Contains all information an agent needs to operate.
    Built by the orchestrator before calling any agent.
    """
    user_id: str
    task_id: Optional[str] = None

    # Genome-derived behavioral context (compressed string for prompt injection)
    genome_context: str = Field(default="No genome data available yet")

    # Calendar and workload context
    calendar_events: list[CalendarEvent] = Field(default_factory=list)
    active_task_count: int = Field(default=0)
    active_task_titles: list[str] = Field(default_factory=list)

    # Time context
    current_time_iso: str = Field(default="")
    user_timezone: str = Field(default="UTC")
    working_hours_start: str = Field(default="09:00")
    working_hours_end: str = Field(default="17:00")

    # Task-specific context (populated when task_id is set)
    task_title: Optional[str] = None
    task_description: Optional[str] = None
    task_deadline: Optional[str] = None
    task_estimated_hours: Optional[float] = None
    task_complexity: Optional[str] = None
    task_category: Optional[str] = None
    task_progress: Optional[float] = None
    task_status: Optional[str] = None

    # Additional data passed by specific orchestration flows
    extra: dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    """
    Standardized result from any agent execution.
    Agents always return this — they never raise exceptions.
    """
    agent_name: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None

    @classmethod
    def success_result(
        cls,
        agent_name: str,
        data: Any,
    ) -> "AgentResult":
        return cls(agent_name=agent_name, success=True, data=data)

    @classmethod
    def failure_result(
        cls,
        agent_name: str,
        error: str,
    ) -> "AgentResult":
        return cls(agent_name=agent_name, success=False, error=error)