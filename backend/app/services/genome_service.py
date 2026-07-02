"""
SPARK — Genome Service
Business logic for the Completion Genome.
Provides compressed context for agent prompts and manages genome updates.
"""

from typing import Optional

from app.core.logging import get_logger
from app.models.genome import CompletionGenome
from app.repositories.genome_repository import GenomeRepository

logger = get_logger(__name__)


class GenomeService:
    """Manages the Completion Genome lifecycle."""

    def __init__(self) -> None:
        self._genome_repo = GenomeRepository()

    def get_genome(self, user_id: str) -> CompletionGenome:
        """
        Returns the user's genome, creating a default one if needed.
        Always returns a genome — never None.
        """
        return self._genome_repo.get_or_create_default(user_id)

    def get_compressed_context(self, user_id: str) -> str:
        """
        Returns a compressed string representation of the genome
        for injection into agent prompts.
        Keeps token usage under 100 tokens while preserving behavioral signals.
        """
        genome = self.get_genome(user_id)
        return genome.to_compressed_context()

    def update_genome(self, user_id: str, genome: CompletionGenome) -> None:
        """Saves an updated genome."""
        self._genome_repo.save(user_id, genome)

    def update_fields(self, user_id: str, updates: dict) -> None:
        """
        Partially updates specific genome fields using dot notation.
        Used by the Reflection Agent for targeted behavioral updates.
        """
        self._genome_repo.update_fields(user_id, updates)
        logger.info(
            "Genome fields updated",
            user_id=user_id,
            field_count=len(updates),
        )

    def record_task_completion(
        self,
        user_id: str,
        succeeded: bool,
        deadline_met: bool,
    ) -> None:
        """
        Updates genome completion statistics after a task finishes.
        Increments counters, updates success rate, manages streaks.
        """
        self._genome_repo.increment_completion_stats(
            user_id=user_id,
            succeeded=succeeded,
            deadline_met=deadline_met,
        )
        logger.info(
            "Genome completion stats updated",
            user_id=user_id,
            succeeded=succeeded,
            deadline_met=deadline_met,
        )

    def get_working_hours(self, user_id: str) -> tuple[float, float]:
        """
        Returns the user's available productive hours per day
        based on their genome and settings.
        Returns (hours_per_day, productive_ratio).
        """
        genome = self.get_genome(user_id)

        # Use optimal session length and focus duration to estimate
        avg_focus = genome.productivity.averageFocusDuration  # minutes
        recovery = genome.productivity.recoveryTimeNeeded  # minutes
        sessions_per_day = 6  # reasonable default

        productive_minutes = sessions_per_day * avg_focus
        total_minutes = sessions_per_day * (avg_focus + recovery)
        hours_per_day = productive_minutes / 60
        productive_ratio = productive_minutes / max(total_minutes, 1)

        return round(hours_per_day, 1), round(productive_ratio, 2)