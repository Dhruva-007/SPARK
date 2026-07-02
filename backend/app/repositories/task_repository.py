"""
SPARK — Task Repository
All Firestore operations for tasks.
Tasks are stored in the top-level /tasks collection, scoped by userId.
"""

from datetime import datetime, timezone
from typing import Optional

from app.core.exceptions import TaskNotFoundError
from app.core.logging import get_logger
from app.models.task import Task, CreateTaskRequest, UpdateTaskRequest
from app.models.cms import CMSCalculationResult, PONRCalculationResult
from app.repositories.base_repository import BaseRepository

logger = get_logger(__name__)

_COLLECTION = "tasks"


class TaskRepository(BaseRepository):
    """Repository for all task Firestore operations."""

    def create(self, task: Task) -> Task:
        """
        Creates a new task document in Firestore.
        Returns the created task with its generated ID.
        """
        data = task.to_firestore()
        self._set_document(_COLLECTION, task.id, data)
        logger.info("Task created", task_id=task.id, user_id=task.userId)
        return task

    def get_by_id(self, task_id: str, user_id: str) -> Task:
        """
        Fetches a task by ID, scoped to the user for security.
        Raises TaskNotFoundError if not found or belongs to different user.
        """
        data = self._get_document(_COLLECTION, task_id, "Task")

        # Security: verify task belongs to the requesting user
        if data.get("userId") != user_id:
            raise TaskNotFoundError(task_id)

        return Task.model_validate(data)

    def list_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> list[Task]:
        """
        Lists all tasks for a user, with optional status filter.
        Ordered by createdAt descending (newest first).
        """
        filters: list[tuple] = [("userId", "==", user_id)]

        if status:
            filters.append(("status", "==", status))

        docs = self._query_collection(
            _COLLECTION,
            filters=filters,
            order_by="createdAt",
            limit=limit,
            descending=True,
        )

        tasks = []
        for doc in docs:
            try:
                tasks.append(Task.model_validate(doc))
            except Exception as exc:
                logger.warning(
                    "Task document failed validation — skipping",
                    task_id=doc.get("id"),
                    error=str(exc),
                )

        return tasks

    def list_active_by_user(self, user_id: str) -> list[Task]:
        """
        Returns all non-completed tasks for a user.
        Used by the CMS worker to recalculate scores.
        """
        filters = [
            ("userId", "==", user_id),
        ]

        docs = self._query_collection(
            _COLLECTION,
            filters=filters,
            order_by="deadline",
            descending=False,
        )

        active_statuses = {"pending", "active", "in_progress"}
        tasks = []
        for doc in docs:
            if doc.get("status") in active_statuses:
                try:
                    tasks.append(Task.model_validate(doc))
                except Exception as exc:
                    logger.warning(
                        "Active task validation failed — skipping",
                        task_id=doc.get("id"),
                        error=str(exc),
                    )

        return tasks

    def update(
        self,
        task_id: str,
        user_id: str,
        updates: dict,
    ) -> None:
        """
        Partially updates a task document.
        Always updates the updatedAt timestamp.
        Verifies task ownership before updating.
        """
        # Verify ownership
        self.get_by_id(task_id, user_id)

        updates["updatedAt"] = datetime.now(timezone.utc).isoformat()
        self._update_document(_COLLECTION, task_id, updates)
        logger.info("Task updated", task_id=task_id, fields=list(updates.keys()))

    def update_progress(
        self,
        task_id: str,
        user_id: str,
        percentage: float,
        milestones_current: int,
        milestones_total: int,
    ) -> None:
        """Updates task progress fields atomically."""
        now = datetime.now(timezone.utc).isoformat()
        self.update(
            task_id,
            user_id,
            {
                "progress.percentage": percentage,
                "progress.lastUpdatedAt": now,
                "progress.milestonesCurrent": milestones_current,
                "progress.milestonesTotal": milestones_total,
                "status": "in_progress" if percentage > 0 else "active",
            },
        )

    def update_cms(
        self,
        task_id: str,
        cms_result: CMSCalculationResult,
    ) -> None:
        """
        Updates CMS fields from a calculation result.
        Called by the CMS worker every 15 minutes.
        Does not verify ownership — called by background workers.
        """
        updates = {
            "cms.score": cms_result.score,
            "cms.momentum": cms_result.momentum,
            "cms.failureRisk": cms_result.failure_risk,
            "cms.completionProbability": cms_result.completion_probability,
            "cms.trend": cms_result.trend,
            "cms.lastCalculatedAt": cms_result.calculated_at,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }
        self._update_document(_COLLECTION, task_id, updates)

    def update_ponr(
        self,
        task_id: str,
        ponr_result: PONRCalculationResult,
    ) -> None:
        """
        Updates PONR fields from a calculation result.
        Called by the PONR worker every 30 minutes.
        """
        updates = {
            "ponr.calculatedAt": ponr_result.calculated_at,
            "ponr.ponrTime": ponr_result.ponr_time,
            "ponr.ponrPassed": ponr_result.ponr_passed,
            "ponr.remainingWorkHours": ponr_result.remaining_work_hours,
            "ponr.remainingAvailableHours": ponr_result.remaining_available_hours,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }
        self._update_document(_COLLECTION, task_id, updates)

    def update_activation(
        self,
        task_id: str,
        google_doc_id: Optional[str],
        google_doc_url: Optional[str],
        checklist_generated: bool,
        outline_generated: bool,
    ) -> None:
        """
        Updates task activation fields after the Activation Agent completes.
        """
        now = datetime.now(timezone.utc).isoformat()
        updates = {
            "activation.isActivated": True,
            "activation.googleDocId": google_doc_id,
            "activation.googleDocUrl": google_doc_url,
            "activation.checklistGenerated": checklist_generated,
            "activation.outlineGenerated": outline_generated,
            "activation.activatedAt": now,
            "status": "active",
            "updatedAt": now,
        }
        self._update_document(_COLLECTION, task_id, updates)

    def mark_complete(self, task_id: str, user_id: str) -> None:
        """Marks a task as completed with timestamp."""
        now = datetime.now(timezone.utc).isoformat()
        self.update(
            task_id,
            user_id,
            {
                "status": "completed",
                "completedAt": now,
                "progress.percentage": 100.0,
            },
        )
        logger.info("Task marked complete", task_id=task_id)

    def mark_bankrupt(self, task_id: str) -> None:
        """Marks a task as bankrupt (sacrificed by the Bankruptcy Engine)."""
        self._update_document(
            _COLLECTION,
            task_id,
            {
                "status": "bankrupt",
                "updatedAt": datetime.now(timezone.utc).isoformat(),
            },
        )

    def delete(self, task_id: str, user_id: str) -> None:
        """Deletes a task after verifying ownership."""
        self.get_by_id(task_id, user_id)
        self._delete_document(_COLLECTION, task_id)
        logger.info("Task deleted", task_id=task_id)