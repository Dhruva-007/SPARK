"""
SPARK — Milestone Repository
All Firestore operations for task milestones.
Milestones are stored in /tasks/{taskId}/milestones/{milestoneId}.
"""

from datetime import datetime, timezone
from typing import Optional

from app.core.logging import get_logger
from app.models.milestone import Milestone
from app.repositories.base_repository import BaseRepository

logger = get_logger(__name__)

_PARENT_COLLECTION = "tasks"
_SUBCOLLECTION = "milestones"


class MilestoneRepository(BaseRepository):
    """Repository for milestone Firestore operations."""

    def batch_create(self, milestones: list[Milestone]) -> list[Milestone]:
        """
        Creates multiple milestones atomically in a single batch write.
        Used when the Planner Agent generates the initial milestone set.
        """
        if not milestones:
            return []

        operations = []
        for milestone in milestones:
            collection_path = (
                f"{_PARENT_COLLECTION}/{milestone.taskId}/{_SUBCOLLECTION}"
            )
            operations.append((collection_path, milestone.id, milestone.to_firestore()))

        self._batch_set(operations)
        logger.info(
            "Milestones batch created",
            task_id=milestones[0].taskId,
            count=len(milestones),
        )
        return milestones

    def create(self, milestone: Milestone) -> Milestone:
        """Creates a single milestone."""
        collection_path = (
            f"{_PARENT_COLLECTION}/{milestone.taskId}/{_SUBCOLLECTION}"
        )
        self._set_document(collection_path, milestone.id, milestone.to_firestore())
        return milestone

    def list_by_task(self, task_id: str) -> list[Milestone]:
        """
        Lists all milestones for a task, ordered by sequence.
        """
        docs = self._subcollection_query(
            parent_collection=_PARENT_COLLECTION,
            parent_id=task_id,
            subcollection=_SUBCOLLECTION,
            order_by="order",
            descending=False,
        )

        milestones = []
        for doc in docs:
            try:
                milestones.append(Milestone.model_validate(doc))
            except Exception as exc:
                logger.warning(
                    "Milestone validation failed — skipping",
                    milestone_id=doc.get("id"),
                    error=str(exc),
                )

        return milestones

    def get_next_action(self, task_id: str) -> Optional[Milestone]:
        """
        Returns the milestone currently marked as the next action.
        Returns the first pending milestone if none is marked.
        """
        docs = self._subcollection_query(
            parent_collection=_PARENT_COLLECTION,
            parent_id=task_id,
            subcollection=_SUBCOLLECTION,
            filters=[("isNextAction", "==", True)],
            limit=1,
        )

        if docs:
            return Milestone.model_validate(docs[0])

        # Fall back to first pending milestone
        pending = self._subcollection_query(
            parent_collection=_PARENT_COLLECTION,
            parent_id=task_id,
            subcollection=_SUBCOLLECTION,
            filters=[("status", "==", "pending")],
            order_by="order",
            limit=1,
        )

        return Milestone.model_validate(pending[0]) if pending else None

    def complete_milestone(self, task_id: str, milestone_id: str) -> None:
        """
        Marks a milestone as completed and clears the next-action flag.
        """
        now = datetime.now(timezone.utc).isoformat()
        collection_path = (
            f"{_PARENT_COLLECTION}/{task_id}/{_SUBCOLLECTION}"
        )
        self._update_document(
            collection_path,
            milestone_id,
            {
                "status": "completed",
                "isNextAction": False,
                "completedAt": now,
            },
        )
        logger.info("Milestone completed", task_id=task_id, milestone_id=milestone_id)

    def set_next_action(self, task_id: str, milestone_id: str) -> None:
        """
        Marks a specific milestone as the current next action.
        First clears any existing next-action flag on other milestones.
        """
        # Clear all existing next-action flags for this task
        all_milestones = self.list_by_task(task_id)
        collection_path = f"{_PARENT_COLLECTION}/{task_id}/{_SUBCOLLECTION}"

        for ms in all_milestones:
            if ms.isNextAction and ms.id != milestone_id:
                self._update_document(
                    collection_path,
                    ms.id,
                    {"isNextAction": False},
                )

        # Set the new next action
        self._update_document(
            collection_path,
            milestone_id,
            {"isNextAction": True, "status": "in_progress"},
        )

    def update(
        self,
        task_id: str,
        milestone_id: str,
        updates: dict,
    ) -> None:
        """Partially updates a milestone."""
        collection_path = f"{_PARENT_COLLECTION}/{task_id}/{_SUBCOLLECTION}"
        self._update_document(collection_path, milestone_id, updates)

    def delete_all_for_task(self, task_id: str) -> None:
        """
        Deletes all milestones for a task.
        Called when a task is deleted.
        """
        milestones = self.list_by_task(task_id)
        collection_path = f"{_PARENT_COLLECTION}/{task_id}/{_SUBCOLLECTION}"

        for ms in milestones:
            self._delete_document(collection_path, ms.id)

        logger.info(
            "All milestones deleted for task",
            task_id=task_id,
            count=len(milestones),
        )