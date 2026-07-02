"""
SPARK — Intervention Repository
All Firestore operations for interventions and reflections.
Interventions: /tasks/{taskId}/interventions/{interventionId}
Reflections:   /users/{userId}/reflections/{reflectionId}
"""

from datetime import datetime, timezone
from typing import Optional

from app.core.logging import get_logger
from app.models.intervention import Intervention, Reflection
from app.repositories.base_repository import BaseRepository

logger = get_logger(__name__)


class InterventionRepository(BaseRepository):
    """Repository for intervention and reflection Firestore operations."""

    # ── Interventions ─────────────────────────────────────────

    def create_intervention(self, intervention: Intervention) -> Intervention:
        """Creates a new intervention record."""
        collection_path = f"tasks/{intervention.taskId}/interventions"
        self._set_document(
            collection_path,
            intervention.id,
            intervention.to_firestore(),
        )
        logger.info(
            "Intervention created",
            intervention_id=intervention.id,
            task_id=intervention.taskId,
            level=intervention.level,
        )
        return intervention

    def list_by_task(
        self,
        task_id: str,
        resolved: Optional[bool] = None,
    ) -> list[Intervention]:
        """Lists interventions for a task, optionally filtered by resolved status."""
        filters: list[tuple] = []
        if resolved is not None:
            if resolved:
                filters.append(("resolvedAt", "!=", None))
            else:
                filters.append(("resolvedAt", "==", None))

        docs = self._subcollection_query(
            parent_collection="tasks",
            parent_id=task_id,
            subcollection="interventions",
            filters=filters if filters else None,
            order_by="createdAt",
            descending=True,
        )

        interventions = []
        for doc in docs:
            try:
                interventions.append(Intervention.model_validate(doc))
            except Exception as exc:
                logger.warning(
                    "Intervention validation failed",
                    doc_id=doc.get("id"),
                    error=str(exc),
                )

        return interventions

    def resolve_intervention(
        self,
        task_id: str,
        intervention_id: str,
        outcome: str,
    ) -> None:
        """Marks an intervention as resolved with an outcome."""
        collection_path = f"tasks/{task_id}/interventions"
        self._update_document(
            collection_path,
            intervention_id,
            {
                "outcome": outcome,
                "resolvedAt": datetime.now(timezone.utc).isoformat(),
            },
        )

    def update_effectiveness(
        self,
        task_id: str,
        intervention_id: str,
        score: float,
    ) -> None:
        """Updates the effectiveness score after reflection analysis."""
        collection_path = f"tasks/{task_id}/interventions"
        self._update_document(
            collection_path,
            intervention_id,
            {"effectivenessScore": score},
        )

    # ── Reflections ───────────────────────────────────────────

    def create_reflection(self, reflection: Reflection) -> Reflection:
        """Creates a post-task reflection record."""
        collection_path = f"users/{reflection.userId}/reflections"
        self._set_document(
            collection_path,
            reflection.id,
            reflection.to_firestore(),
        )
        logger.info(
            "Reflection created",
            reflection_id=reflection.id,
            user_id=reflection.userId,
            task_id=reflection.taskId,
        )
        return reflection

    def list_reflections(
        self,
        user_id: str,
        limit: int = 20,
    ) -> list[Reflection]:
        """Lists recent reflections for a user."""
        docs = self._subcollection_query(
            parent_collection="users",
            parent_id=user_id,
            subcollection="reflections",
            order_by="createdAt",
            limit=limit,
            descending=True,
        )

        reflections = []
        for doc in docs:
            try:
                reflections.append(Reflection.model_validate(doc))
            except Exception as exc:
                logger.warning(
                    "Reflection validation failed",
                    doc_id=doc.get("id"),
                    error=str(exc),
                )

        return reflections