"""
SPARK — Completion Genome Domain Models
The behavioral intelligence model for each user.
Stored in Firestore /users/{userId}/genome/{genomeId}.
Updated by the Reflection Agent after every completed task.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class GenomeProductivity(BaseModel):
    peakHours: list[int] = Field(default=[9, 10, 14, 15])
    averageFocusDuration: int = Field(default=45)      # minutes
    optimalSessionLength: int = Field(default=90)       # minutes
    recoveryTimeNeeded: int = Field(default=15)         # minutes between sessions


class GenomeEstimation(BaseModel):
    averageUnderestimationFactor: float = Field(default=1.3)
    complexityCalibration: dict[str, float] = Field(
        default={"low": 1.1, "medium": 1.3, "high": 1.6}
    )


class GenomeProcrastination(BaseModel):
    triggers: list[str] = Field(default_factory=list)
    averageDelayDays: float = Field(default=1.0)
    startingDifficulty: float = Field(default=5.0, ge=0, le=10)
    recoveryPattern: str = Field(default="consistent")


class GenomeCompletion(BaseModel):
    successRate: float = Field(default=0.7, ge=0.0, le=1.0)
    totalTasksCompleted: int = Field(default=0, ge=0)
    totalTasksFailed: int = Field(default=0, ge=0)
    averageCompletionAccuracy: float = Field(default=0.7, ge=0.0, le=1.0)
    bestCompletionDayOfWeek: int = Field(default=2, ge=0, le=6)
    streakCurrent: int = Field(default=0, ge=0)
    streakBest: int = Field(default=0, ge=0)


class GenomePreferences(BaseModel):
    taskOrderPreference: str = Field(default="deadline")
    communicationStyle: str = Field(default="direct")
    interventionPreference: str = Field(default="moderate")
    breakFrequency: int = Field(default=45)


class GenomeInterventionHistory(BaseModel):
    totalInterventions: int = Field(default=0, ge=0)
    successfulInterventions: int = Field(default=0, ge=0)
    mostEffectiveLevel: int = Field(default=2, ge=0, le=5)
    leastEffectiveLevel: int = Field(default=0, ge=0, le=5)


class CompletionGenome(BaseModel):
    """
    Complete Completion Genome for a user.
    Stored in /users/{userId}/genome/current.
    """

    version: int = Field(default=1)
    updatedAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    productivity: GenomeProductivity = Field(default_factory=GenomeProductivity)
    estimation: GenomeEstimation = Field(default_factory=GenomeEstimation)
    procrastination: GenomeProcrastination = Field(
        default_factory=GenomeProcrastination
    )
    completion: GenomeCompletion = Field(default_factory=GenomeCompletion)
    preferences: GenomePreferences = Field(default_factory=GenomePreferences)
    interventionHistory: GenomeInterventionHistory = Field(
        default_factory=GenomeInterventionHistory
    )

    @classmethod
    def create_default(cls) -> "CompletionGenome":
        """Creates a default genome for a new user."""
        return cls()

    def to_firestore(self) -> dict:
        return self.model_dump()

    def to_compressed_context(self) -> str:
        """
        Returns a compressed string representation for injection into agent prompts.
        Keeps token usage low while preserving behavioral signals.
        """
        return (
            f"Peak hours: {self.productivity.peakHours} | "
            f"Focus duration: {self.productivity.averageFocusDuration}min | "
            f"Underestimation factor: {self.estimation.averageUnderestimationFactor:.2f} | "
            f"Success rate: {self.completion.successRate:.0%} | "
            f"Delay pattern: {self.procrastination.averageDelayDays:.1f} days avg | "
            f"Procrastination triggers: {', '.join(self.procrastination.triggers) or 'none identified'} | "
            f"Recovery pattern: {self.procrastination.recoveryPattern} | "
            f"Best intervention level: {self.interventionHistory.mostEffectiveLevel} | "
            f"Streak: {self.completion.streakCurrent} tasks"
        )