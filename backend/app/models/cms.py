"""
SPARK — CMS and PONR Models
Data transfer objects for Completion Momentum Score
and Point of No Return calculations.
"""

from typing import Optional
from pydantic import BaseModel, Field


class CMSCalculationResult(BaseModel):
    """Result of a CMS calculation — passed between service and agents."""

    task_id: str
    score: float = Field(ge=0.0, le=100.0)
    momentum: float = Field(ge=0.0, le=100.0)
    failure_risk: float = Field(ge=0.0, le=100.0)
    completion_probability: float = Field(ge=0.0, le=1.0)
    trend: str = Field(default="stable")
    next_action: Optional[str] = Field(default=None)
    calculated_at: str


class PONRCalculationResult(BaseModel):
    """Result of a PONR calculation."""

    task_id: str
    ponr_time: Optional[str] = Field(default=None)
    ponr_passed: bool = Field(default=False)
    hours_until_ponr: Optional[float] = Field(default=None)
    remaining_work_hours: float
    remaining_available_hours: float
    calculated_at: str