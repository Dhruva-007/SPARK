"""
SPARK — PONR Service
Point of No Return calculator.

The PONR is the latest moment at which work must begin (or resume)
for a task to still be completable before its deadline.

PONR = Deadline - (Remaining Work Hours / Productivity Factor)

When PONR is crossed, the system enters Recovery Mode.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.logging import get_logger
from app.models.task import Task
from app.models.cms import PONRCalculationResult
from app.repositories.task_repository import TaskRepository
from app.services.genome_service import GenomeService

logger = get_logger(__name__)


class PONRService:
    """Calculates the Point of No Return for tasks."""

    def __init__(self) -> None:
        self._task_repo = TaskRepository()
        self._genome_service = GenomeService()

    def calculate_ponr(self, task: Task, user_id: str) -> PONRCalculationResult:
        """
        Calculates the PONR for a task based on remaining work
        and the user's productive capacity.
        """
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        # Parse deadline
        try:
            deadline = datetime.fromisoformat(
                task.deadline.replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            return PONRCalculationResult(
                task_id=task.id,
                ponr_time=None,
                ponr_passed=False,
                hours_until_ponr=None,
                remaining_work_hours=task.estimatedHours,
                remaining_available_hours=0,
                calculated_at=now_iso,
            )

        # Calculate remaining work
        progress_fraction = task.progress.percentage / 100
        remaining_work_hours = task.estimatedHours * (1 - progress_fraction)

        # Get user's productive capacity
        hours_per_day, productivity_ratio = self._genome_service.get_working_hours(
            user_id
        )

        # Apply underestimation factor from genome
        genome = self._genome_service.get_genome(user_id)
        underestimation = genome.estimation.averageUnderestimationFactor
        adjusted_remaining = remaining_work_hours * underestimation

        # Calculate how many calendar days of work are needed
        if hours_per_day > 0:
            work_days_needed = adjusted_remaining / hours_per_day
        else:
            work_days_needed = adjusted_remaining / 4  # fallback: 4h/day

        # PONR = deadline - days_needed
        ponr_dt = deadline - timedelta(days=work_days_needed)

        # Hours until deadline for available hours calculation
        hours_until_deadline = max(
            (deadline - now).total_seconds() / 3600, 0
        )

        # Available productive hours = remaining_days * hours_per_day
        remaining_days = hours_until_deadline / 24
        available_hours = remaining_days * hours_per_day

        # Is PONR already passed?
        ponr_passed = now >= ponr_dt

        # Hours until PONR
        hours_until_ponr = max(
            (ponr_dt - now).total_seconds() / 3600, 0
        ) if not ponr_passed else 0

        return PONRCalculationResult(
            task_id=task.id,
            ponr_time=ponr_dt.isoformat() if not ponr_passed else None,
            ponr_passed=ponr_passed,
            hours_until_ponr=round(hours_until_ponr, 1) if not ponr_passed else None,
            remaining_work_hours=round(adjusted_remaining, 1),
            remaining_available_hours=round(available_hours, 1),
            calculated_at=now_iso,
        )

    def recalculate_for_task(
        self, task_id: str, user_id: str
    ) -> PONRCalculationResult:
        """Calculates PONR for a single task and persists the result."""
        task = self._task_repo.get_by_id(task_id, user_id)
        result = self.calculate_ponr(task, user_id)
        self._task_repo.update_ponr(task_id, result)

        if result.ponr_passed:
            logger.warning(
                "PONR has passed for task",
                task_id=task_id,
                user_id=user_id,
            )
            # TODO Phase 13: Trigger recovery intervention

        return result

    def scan_all_for_user(self, user_id: str) -> list[PONRCalculationResult]:
        """
        Scans all active tasks for PONR status.
        Called by the PONR worker every 30 minutes.
        """
        tasks = self._task_repo.list_active_by_user(user_id)
        results = []

        for task in tasks:
            try:
                result = self.calculate_ponr(task, user_id)
                self._task_repo.update_ponr(task.id, result)
                results.append(result)

                if result.ponr_passed:
                    logger.warning("PONR passed", task_id=task.id)

            except Exception as exc:
                logger.error(
                    "PONR calculation failed",
                    task_id=task.id,
                    error=str(exc),
                )

        return results  