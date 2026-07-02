"""
SPARK — Long-Term Memory
Permanent behavioral intelligence built from the Completion Genome.

Long-term memory is not a separate storage layer — it IS the genome.
This module provides the interface between the Memory Engine and
the GenomeService, adding memory-specific operations like:

- Historical task pattern analysis
- Behavioral trend detection
- Intervention effectiveness learning
- Estimation accuracy tracking over time

All writes go through GenomeService → GenomeRepository.
This module only adds analysis and compression logic.
"""

from datetime import datetime, timezone
from typing import Optional

from app.core.logging import get_logger
from app.models.genome import CompletionGenome
from app.services.genome_service import GenomeService

logger = get_logger(__name__)


class LongTermMemory:
    """
    Interface to the permanent behavioral memory (Completion Genome).
    Provides analysis and compression utilities on top of GenomeService.
    """

    def __init__(self) -> None:
        self._genome_service = GenomeService()

    def get_genome(self, user_id: str) -> CompletionGenome:
        """Returns the user's Completion Genome."""
        return self._genome_service.get_genome(user_id)

    def get_behavioral_summary(self, user_id: str) -> dict:
        """
        Returns a structured behavioral summary derived from the genome.
        Used by MemoryAgent to build rich agent context.
        """
        genome = self.get_genome(user_id)

        # Determine productivity window
        peak_hours = genome.productivity.peakHours
        if peak_hours:
            peak_start = min(peak_hours)
            peak_end = max(peak_hours)
            productivity_window = f"{peak_start:02d}:00–{peak_end:02d}:59"
        else:
            productivity_window = "Unknown"

        # Current hour analysis
        current_hour = datetime.now(timezone.utc).hour
        is_peak_hour = current_hour in peak_hours

        # Underestimation risk
        underest_factor = genome.estimation.averageUnderestimationFactor
        underestimation_risk = "high" if underest_factor > 1.5 else (
            "moderate" if underest_factor > 1.2 else "low"
        )

        # Streak status
        streak = genome.completion.streakCurrent
        streak_status = (
            "on a streak" if streak >= 3 else
            "building momentum" if streak >= 1 else
            "no current streak"
        )

        # Intervention effectiveness
        best_level = genome.interventionHistory.mostEffectiveLevel
        worst_level = genome.interventionHistory.leastEffectiveLevel

        return {
            "productivity_window": productivity_window,
            "is_peak_hour": is_peak_hour,
            "current_hour": current_hour,
            "focus_duration_minutes": genome.productivity.averageFocusDuration,
            "recovery_time_minutes": genome.productivity.recoveryTimeNeeded,
            "underestimation_factor": underest_factor,
            "underestimation_risk": underestimation_risk,
            "success_rate": genome.completion.successRate,
            "total_completed": genome.completion.totalTasksCompleted,
            "streak_current": streak,
            "streak_status": streak_status,
            "procrastination_triggers": genome.procrastination.triggers,
            "recovery_pattern": genome.procrastination.recoveryPattern,
            "preferred_intervention_level": best_level,
            "ineffective_intervention_level": worst_level,
            "communication_style": genome.preferences.communicationStyle,
        }

    def compress_for_prompt(self, user_id: str) -> str:
        """
        Returns an optimized string for agent prompt injection.
        Target: under 150 tokens while preserving key behavioral signals.
        """
        genome = self.get_genome(user_id)
        return genome.to_compressed_context()

    def update_intervention_effectiveness(
        self,
        user_id: str,
        level: int,
        was_effective: bool,
    ) -> None:
        """
        Updates the genome's intervention effectiveness tracking.
        Called after an intervention is resolved with an outcome.
        """
        genome = self.get_genome(user_id)
        history = genome.interventionHistory

        history.totalInterventions += 1
        if was_effective:
            history.successfulInterventions += 1
            # Update most effective level with exponential moving average
            # (bias toward recent data, not just all-time)
            if was_effective and (
                history.totalInterventions < 5 or
                level == history.mostEffectiveLevel
            ):
                history.mostEffectiveLevel = level
        else:
            if level == history.leastEffectiveLevel or history.totalInterventions < 3:
                history.leastEffectiveLevel = level

        genome.interventionHistory = history
        self._genome_service.update_genome(user_id, genome)

        logger.info(
            "Intervention effectiveness updated",
            user_id=user_id,
            level=level,
            was_effective=was_effective,
        )

    def record_estimation_result(
        self,
        user_id: str,
        estimated_hours: float,
        actual_hours: float,
        complexity: str,
    ) -> None:
        """
        Updates the genome's estimation calibration based on a completed task.
        Uses exponential moving average to weight recent tasks more.
        """
        if actual_hours <= 0 or estimated_hours <= 0:
            return

        actual_ratio = actual_hours / estimated_hours
        genome = self.get_genome(user_id)

        # EMA with alpha=0.3 (30% new data, 70% historical)
        alpha = 0.3
        current_factor = genome.estimation.averageUnderestimationFactor
        new_factor = alpha * actual_ratio + (1 - alpha) * current_factor
        genome.estimation.averageUnderestimationFactor = round(new_factor, 3)

        # Update complexity-specific calibration
        if complexity in genome.estimation.complexityCalibration:
            current_calib = genome.estimation.complexityCalibration[complexity]
            new_calib = alpha * actual_ratio + (1 - alpha) * current_calib
            genome.estimation.complexityCalibration[complexity] = round(new_calib, 3)

        self._genome_service.update_genome(user_id, genome)

        logger.info(
            "Estimation calibration updated",
            user_id=user_id,
            estimated=estimated_hours,
            actual=actual_hours,
            ratio=round(actual_ratio, 3),
            new_factor=genome.estimation.averageUnderestimationFactor,
        )

    def update_peak_hours(
        self,
        user_id: str,
        productive_hours: list[int],
    ) -> None:
        """
        Updates the genome's peak productivity hours.
        Called by ReflectionAgent after analyzing when work was done.
        """
        if not productive_hours:
            return

        genome = self.get_genome(user_id)
        current_peaks = set(genome.productivity.peakHours)

        # Merge new productive hours with existing peaks
        # Keep the top 6 most frequently observed hours
        all_hours = list(current_peaks | set(productive_hours))
        # Bias toward hours that appear in both current and new
        weighted = [
            h for h in all_hours
            if h in current_peaks and h in productive_hours
        ] + [
            h for h in all_hours
            if h not in current_peaks or h not in productive_hours
        ]

        genome.productivity.peakHours = sorted(set(weighted[:8]))
        self._genome_service.update_genome(user_id, genome)

        logger.info(
            "Peak hours updated",
            user_id=user_id,
            new_peaks=genome.productivity.peakHours,
        )