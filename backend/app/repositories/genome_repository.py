"""
SPARK — Genome Repository
All Firestore operations for the Completion Genome.
Stored in /users/{userId}/genome/current (single document per user).
The 'current' document is always the live genome.
Version history is not stored — genome evolves in place.
"""

from typing import Optional

from app.core.logging import get_logger
from app.models.genome import CompletionGenome
from app.repositories.base_repository import BaseRepository

logger = get_logger(__name__)

_GENOME_DOC_ID = "current"


class GenomeRepository(BaseRepository):
    """Repository for Completion Genome Firestore operations."""

    def _genome_path(self, user_id: str) -> tuple[str, str]:
        """Returns the collection path and document ID for a user's genome."""
        return f"users/{user_id}/genome", _GENOME_DOC_ID

    def get(self, user_id: str) -> Optional[CompletionGenome]:
        """
        Fetches the current genome for a user.
        Returns None if genome has not been initialized yet.
        """
        try:
            collection_path, doc_id = self._genome_path(user_id)
            data = self._get_document(collection_path, doc_id, "Genome")
            return CompletionGenome.model_validate(data)
        except Exception:
            return None

    def get_or_create_default(self, user_id: str) -> CompletionGenome:
        """
        Fetches the genome, creating a default one if it does not exist.
        Used by agents that always need a genome context.
        """
        genome = self.get(user_id)
        if genome is None:
            genome = CompletionGenome.create_default()
            self.save(user_id, genome)
            logger.info("Default genome created", user_id=user_id)
        return genome

    def save(self, user_id: str, genome: CompletionGenome) -> None:
        """
        Saves the genome to Firestore.
        Increments the version number on every save.
        """
        genome.version += 1
        collection_path, doc_id = self._genome_path(user_id)
        self._set_document(collection_path, doc_id, genome.to_firestore())
        logger.info(
            "Genome saved",
            user_id=user_id,
            version=genome.version,
        )

    def update_fields(self, user_id: str, updates: dict) -> None:
        """
        Partially updates specific genome fields.
        Uses Firestore dot notation for nested field updates.
        e.g. {"productivity.averageFocusDuration": 55}
        """
        from datetime import datetime, timezone
        updates["updatedAt"] = datetime.now(timezone.utc).isoformat()

        collection_path, doc_id = self._genome_path(user_id)
        self._update_document(collection_path, doc_id, updates)
        logger.info(
            "Genome fields updated",
            user_id=user_id,
            fields=list(updates.keys()),
        )

    def increment_completion_stats(
        self,
        user_id: str,
        succeeded: bool,
        deadline_met: bool,
    ) -> None:
        """
        Increments completion statistics after a task is finished.
        Called by the Reflection Agent.
        """
        genome = self.get_or_create_default(user_id)

        completion = genome.completion
        if succeeded:
            completion.totalTasksCompleted += 1
            if deadline_met:
                completion.streakCurrent += 1
                completion.streakBest = max(
                    completion.streakBest, completion.streakCurrent
                )
            else:
                completion.streakCurrent = 0
        else:
            completion.totalTasksFailed += 1
            completion.streakCurrent = 0

        total = completion.totalTasksCompleted + completion.totalTasksFailed
        if total > 0:
            completion.successRate = completion.totalTasksCompleted / total

        genome.completion = completion
        self.save(user_id, genome)