"""
SPARK — Task Service
Business logic for the complete task lifecycle.
Planning runs as a background task — creation returns immediately.
"""

import asyncio
from datetime import datetime, timezone
from typing import Optional

from app.core.exceptions import (
    TaskAlreadyCompletedError,
    ValidationError,
)
from app.core.logging import get_logger
from app.models.task import (
    Task,
    CreateTaskRequest,
    UpdateTaskRequest,
    UpdateProgressRequest,
)
from app.models.milestone import Milestone
from app.repositories.task_repository import TaskRepository
from app.repositories.milestone_repository import MilestoneRepository

logger = get_logger(__name__)


class TaskService:
    """Manages the complete task lifecycle."""

    def __init__(self) -> None:
        self._task_repo = TaskRepository()
        self._milestone_repo = MilestoneRepository()

    def create_task(self, user_id: str, request: CreateTaskRequest) -> Task:
        """
        Creates a new task and enqueues planning as a background task.
        Returns immediately — milestones are generated asynchronously.

        The frontend will see milestonesTotal=0 initially, then the
        dashboard auto-refreshes via React Query staleTime.
        """
        # Validate deadline
        try:
            deadline_dt = datetime.fromisoformat(
                request.deadline.replace("Z", "+00:00")
            )
            if deadline_dt <= datetime.now(timezone.utc):
                raise ValidationError("Deadline must be in the future")
        except ValueError:
            raise ValidationError(
                "Invalid deadline format — use ISO datetime string"
            )

        # Validate enums
        valid_categories = {"academic", "work", "personal"}
        valid_priorities = {"critical", "high", "medium", "low"}
        valid_complexities = {"low", "medium", "high"}

        if request.category not in valid_categories:
            raise ValidationError(f"Category must be one of: {valid_categories}")
        if request.priority not in valid_priorities:
            raise ValidationError(f"Priority must be one of: {valid_priorities}")
        if request.complexity not in valid_complexities:
            raise ValidationError(f"Complexity must be one of: {valid_complexities}")

        # Create task
        task = Task.create_new(
            user_id=user_id,
            title=request.title,
            description=request.description,
            category=request.category,
            priority=request.priority,
            deadline=request.deadline,
            estimated_hours=request.estimatedHours,
            complexity=request.complexity,
            tags=request.tags,
        )

        # Store in Firestore — this is fast
        created_task = self._task_repo.create(task)
        logger.info(
            "Task created",
            task_id=created_task.id,
            user_id=user_id,
            title=created_task.title,
        )

        # Enqueue planning as background task — do not wait
        try:
            asyncio.get_event_loop().create_task(
                self._run_planning_background(user_id, created_task.id)
            )
            logger.info("Planning enqueued as background task", task_id=created_task.id)
        except RuntimeError:
            # No event loop — fall back to sync (shouldn't happen in FastAPI)
            logger.warning(
                "No event loop — planning skipped, will run on first CMS calculation",
                task_id=created_task.id,
            )

        return created_task

    async def _run_planning_background(self, user_id: str, task_id: str) -> None:
        """
        Runs PlannerAgent in the background after task creation.
        Errors are logged but never propagate to the user.
        """
        try:
            from app.agents.orchestrator import AgentOrchestrator
            orchestrator = AgentOrchestrator()
            plan_result = await orchestrator.run_task_creation_flow(
                user_id=user_id,
                task_id=task_id,
            )
            logger.info(
                "Background planning complete",
                task_id=task_id,
                milestones=plan_result.get("milestones_created", 0),
            )
        except Exception as exc:
            logger.error(
                "Background planning failed",
                task_id=task_id,
                error=str(exc),
            )

    def get_task(self, task_id: str, user_id: str) -> Task:
        return self._task_repo.get_by_id(task_id, user_id)

    def list_tasks(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[Task]:
        return self._task_repo.list_by_user(user_id, status=status, limit=limit)

    def list_active_tasks(self, user_id: str) -> list[Task]:
        return self._task_repo.list_active_by_user(user_id)

    def update_task(
        self,
        task_id: str,
        user_id: str,
        request: UpdateTaskRequest,
    ) -> Task:
        task = self._task_repo.get_by_id(task_id, user_id)

        if task.status in ("completed", "bankrupt"):
            raise TaskAlreadyCompletedError(task_id)

        updates: dict = {}
        if request.title is not None:
            updates["title"] = request.title
        if request.description is not None:
            updates["description"] = request.description
        if request.priority is not None:
            valid_priorities = {"critical", "high", "medium", "low"}
            if request.priority not in valid_priorities:
                raise ValidationError(
                    f"Priority must be one of: {valid_priorities}"
                )
            updates["priority"] = request.priority
        if request.deadline is not None:
            try:
                deadline_dt = datetime.fromisoformat(
                    request.deadline.replace("Z", "+00:00")
                )
                if deadline_dt <= datetime.now(timezone.utc):
                    raise ValidationError("Deadline must be in the future")
            except ValueError:
                raise ValidationError("Invalid deadline format")
            updates["deadline"] = request.deadline
        if request.estimatedHours is not None:
            updates["estimatedHours"] = request.estimatedHours
        if request.tags is not None:
            updates["tags"] = request.tags

        if updates:
            self._task_repo.update(task_id, user_id, updates)

        return self._task_repo.get_by_id(task_id, user_id)

    def update_progress(
        self,
        task_id: str,
        user_id: str,
        request: UpdateProgressRequest,
    ) -> Task:
        task = self._task_repo.get_by_id(task_id, user_id)

        if task.status in ("completed", "bankrupt"):
            raise TaskAlreadyCompletedError(task_id)

        milestones = self._milestone_repo.list_by_task(task_id)
        milestones_total = len(milestones)
        milestones_completed = sum(
            1 for m in milestones if m.status == "completed"
        )

        self._task_repo.update_progress(
            task_id=task_id,
            user_id=user_id,
            percentage=request.percentage,
            milestones_current=milestones_completed,
            milestones_total=milestones_total,
        )

        return self._task_repo.get_by_id(task_id, user_id)

    async def complete_task(self, task_id: str, user_id: str) -> Task:
        """Marks a task as completed and triggers reflection in background."""
        task = self._task_repo.get_by_id(task_id, user_id)

        if task.status == "completed":
            raise TaskAlreadyCompletedError(task_id)

        self._task_repo.mark_complete(task_id, user_id)
        logger.info("Task completed", task_id=task_id, user_id=user_id)

        # Run reflection in background — don't block the response
        try:
            asyncio.get_event_loop().create_task(
                self._run_reflection_background(task_id, user_id)
            )
        except Exception as exc:
            logger.warning("Could not enqueue reflection", error=str(exc))

        # Record in memory
        try:
            from app.memory.short_term import ShortTermMemory
            stm = ShortTermMemory()
            stm.record(
                user_id=user_id,
                observation_type="task_completed",
                data={"task_title": task.title},
                task_id=task_id,
            )
        except Exception:
            pass

        return self._task_repo.get_by_id(task_id, user_id)

    async def _run_reflection_background(self, task_id: str, user_id: str) -> None:
        """Runs ReflectionAgent in background after task completion."""
        try:
            from app.services.reflection_service import ReflectionService
            reflection_service = ReflectionService()
            completed_task = self._task_repo.get_by_id(task_id, user_id)
            await reflection_service.create_reflection(completed_task, user_id)
        except Exception as exc:
            logger.warning(
                "Background reflection failed",
                task_id=task_id,
                error=str(exc),
            )

    def delete_task(self, task_id: str, user_id: str) -> None:
        self._task_repo.get_by_id(task_id, user_id)
        self._milestone_repo.delete_all_for_task(task_id)
        self._task_repo.delete(task_id, user_id)
        logger.info("Task deleted", task_id=task_id)

    def get_milestones(self, task_id: str, user_id: str) -> list[Milestone]:
        self._task_repo.get_by_id(task_id, user_id)
        return self._milestone_repo.list_by_task(task_id)

    def complete_milestone(
        self,
        task_id: str,
        milestone_id: str,
        user_id: str,
    ) -> list[Milestone]:
        self._task_repo.get_by_id(task_id, user_id)
        self._milestone_repo.complete_milestone(task_id, milestone_id)

        milestones = self._milestone_repo.list_by_task(task_id)
        total = len(milestones)
        completed = sum(1 for m in milestones if m.status == "completed")

        next_pending = next(
            (m for m in milestones if m.status == "pending"),
            None,
        )
        if next_pending:
            self._milestone_repo.set_next_action(task_id, next_pending.id)

        if total > 0:
            percentage = (completed / total) * 100
            self._task_repo.update_progress(
                task_id=task_id,
                user_id=user_id,
                percentage=percentage,
                milestones_current=completed,
                milestones_total=total,
            )

        return milestones