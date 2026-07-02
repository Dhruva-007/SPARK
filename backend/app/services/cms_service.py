"""
SPARK — CMS Service
Completion Momentum Score calculation engine.

The CMS is calculated from a mathematical baseline combined with
a qualitative AI adjustment from the Momentum Agent.

Mathematical baseline considers:
- Progress velocity (progress_pct / hours_elapsed)
- Expected vs actual progress at this point in time
- Time pressure (hours_remaining / hours_total)
- Effort feasibility (remaining_work / remaining_time)

The AI adjustment considers:
- User behavioral patterns from the Completion Genome
- Historical accuracy for this task type
- Procrastination patterns

Phase 12 adds the full AI adjustment via MomentumAgent.
This phase implements the complete mathematical engine.
"""

from datetime import datetime, timezone
from typing import Optional

from app.core.logging import get_logger
from app.models.task import Task
from app.models.cms import CMSCalculationResult
from app.repositories.task_repository import TaskRepository

logger = get_logger(__name__)


class CMSService:
    """Calculates Completion Momentum Scores for tasks."""

    def __init__(self) -> None:
        self._task_repo = TaskRepository()

    def calculate_cms(
        self,
        task: Task,
        ai_adjustment: float = 0.0,
    ) -> CMSCalculationResult:
        """
        Calculates the Completion Momentum Score for a single task.

        The CMS is a 0-100 score that represents the probability
        of completing the task before its deadline.

        Components:
        1. Progress score (0-40): how much work is done
        2. Velocity score (0-30): is progress on track
        3. Feasibility score (0-30): can remaining work fit in remaining time
        4. AI adjustment (-20 to +20): behavioral pattern modifier

        Args:
            task: The task to calculate CMS for
            ai_adjustment: Modifier from the Momentum Agent (-20 to +20)

        Returns:
            CMSCalculationResult with all calculated fields
        """
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        # Parse timestamps
        try:
            created = datetime.fromisoformat(
                task.createdAt.replace("Z", "+00:00")
            )
            deadline = datetime.fromisoformat(
                task.deadline.replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            logger.warning("Invalid dates in task — returning default CMS", task_id=task.id)
            return CMSCalculationResult(
                task_id=task.id,
                score=50.0,
                momentum=0.0,
                failure_risk=50.0,
                completion_probability=0.5,
                trend="stable",
                calculated_at=now_iso,
            )

        # Time calculations
        total_duration = (deadline - created).total_seconds() / 3600  # hours
        hours_elapsed = (now - created).total_seconds() / 3600
        hours_remaining = max((deadline - now).total_seconds() / 3600, 0)

        # Avoid division by zero
        total_duration = max(total_duration, 0.1)
        hours_elapsed = max(hours_elapsed, 0.01)

        progress = task.progress.percentage
        estimated_hours = task.estimatedHours
        remaining_work_hours = estimated_hours * (1 - progress / 100)

        # ── Component 1: Progress Score (0-40) ─────────────────
        # Simple: what percentage of work is done
        progress_score = (progress / 100) * 40

        # ── Component 2: Velocity Score (0-30) ─────────────────
        # Is progress on track relative to time elapsed?
        time_fraction = hours_elapsed / total_duration
        expected_progress = time_fraction * 100  # linear expectation
        velocity_ratio = progress / max(expected_progress, 1)
        # velocity_ratio > 1 means ahead of schedule
        # velocity_ratio < 1 means behind schedule
        velocity_score = min(velocity_ratio, 2.0) / 2.0 * 30

        # ── Component 3: Feasibility Score (0-30) ──────────────
        # Can the remaining work fit in the remaining time?
        if hours_remaining <= 0:
            feasibility_score = 0.0 if progress < 100 else 30.0
        elif remaining_work_hours <= 0:
            feasibility_score = 30.0
        else:
            feasibility_ratio = hours_remaining / remaining_work_hours
            # feasibility > 1 means enough time
            # feasibility < 1 means not enough time
            feasibility_clamped = min(feasibility_ratio, 3.0) / 3.0
            feasibility_score = feasibility_clamped * 30

        # ── Combine ────────────────────────────────────────────
        raw_score = progress_score + velocity_score + feasibility_score
        adjusted_score = max(0, min(100, raw_score + ai_adjustment))

        # ── Derived metrics ────────────────────────────────────
        momentum = max(0, min(100, velocity_score / 30 * 100))

        failure_risk = max(0, min(100, 100 - adjusted_score))

        completion_probability = max(0.0, min(1.0, adjusted_score / 100))

        # ── Trend determination ────────────────────────────────
        prev_score = task.cms.score
        if adjusted_score > prev_score + 5:
            trend = "improving"
        elif adjusted_score < prev_score - 10:
            trend = "critical" if adjusted_score < 30 else "declining"
        else:
            trend = "stable"

        return CMSCalculationResult(
            task_id=task.id,
            score=round(adjusted_score, 1),
            momentum=round(momentum, 1),
            failure_risk=round(failure_risk, 1),
            completion_probability=round(completion_probability, 3),
            trend=trend,
            calculated_at=now_iso,
        )

    def recalculate_for_task(self, task_id: str, user_id: str) -> CMSCalculationResult:
        """
        Recalculates CMS for a single task and persists the result.
        """
        task = self._task_repo.get_by_id(task_id, user_id)

        # TODO Phase 12: Get AI adjustment from MomentumAgent
        ai_adjustment = 0.0

        result = self.calculate_cms(task, ai_adjustment)
        self._task_repo.update_cms(task_id, result)

        logger.info(
            "CMS recalculated",
            task_id=task_id,
            score=result.score,
            risk=result.failure_risk,
            trend=result.trend,
        )

        return result

    def recalculate_all_for_user(self, user_id: str) -> list[CMSCalculationResult]:
        """
        Recalculates CMS for all active tasks belonging to a user.
        Called by the CMS worker every 15 minutes.
        """
        tasks = self._task_repo.list_active_by_user(user_id)
        results = []

        for task in tasks:
            try:
                result = self.calculate_cms(task)
                self._task_repo.update_cms(task.id, result)
                results.append(result)
            except Exception as exc:
                logger.error(
                    "CMS recalculation failed for task",
                    task_id=task.id,
                    error=str(exc),
                )

        logger.info(
            "Batch CMS recalculation complete",
            user_id=user_id,
            tasks_processed=len(results),
        )

        return results