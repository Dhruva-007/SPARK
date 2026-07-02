"""
SPARK — Short-Term Memory
Session-scoped observations stored in Firestore.
TTL: 24 hours — cleared automatically by a daily Cloud Scheduler job.

Short-term memory tracks what happened in the current work session:
- Which tasks are currently in focus
- Recent interventions and their outcomes
- Progress events in the last 24 hours
- User response patterns within the session
- Agent decisions made recently

This is NOT the Completion Genome — that is long-term memory.
Short-term memory is ephemeral context that makes agents aware
of what just happened, preventing repeated interventions and
enabling session continuity.

Firestore path: /sessions/{userId}/observations/{observationId}
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from app.core.logging import get_logger
from app.repositories.base_repository import BaseRepository

logger = get_logger(__name__)

_COLLECTION = "sessions"
_SUBCOLLECTION = "observations"

# Observation type constants
OBS_TASK_FOCUSED = "task_focused"
OBS_TASK_PROGRESS = "task_progress"
OBS_INTERVENTION_FIRED = "intervention_fired"
OBS_INTERVENTION_OUTCOME = "intervention_outcome"
OBS_MILESTONE_COMPLETED = "milestone_completed"
OBS_NEXT_ACTION_VIEWED = "next_action_viewed"
OBS_SESSION_START = "session_start"
OBS_AGENT_RUN = "agent_run"


class Observation:
    """A single short-term memory observation."""

    def __init__(
        self,
        user_id: str,
        observation_type: str,
        data: dict,
        task_id: Optional[str] = None,
    ) -> None:
        self.id = str(uuid4())
        self.user_id = user_id
        self.task_id = task_id
        self.type = observation_type
        self.data = data
        self.created_at = datetime.now(timezone.utc).isoformat()
        # TTL: 24 hours from now
        self.expires_at = (
            datetime.now(timezone.utc) + timedelta(hours=24)
        ).isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "userId": self.user_id,
            "taskId": self.task_id,
            "type": self.type,
            "data": self.data,
            "createdAt": self.created_at,
            "expiresAt": self.expires_at,
        }


class ShortTermMemory(BaseRepository):
    """
    Manages short-term session memory in Firestore.

    Usage:
        stm = ShortTermMemory()
        stm.record(user_id, OBS_TASK_PROGRESS, {"percentage": 45}, task_id)
        recent = stm.get_recent(user_id, limit=20)
        summary = stm.get_session_summary(user_id)
    """

    def record(
        self,
        user_id: str,
        observation_type: str,
        data: dict,
        task_id: Optional[str] = None,
    ) -> None:
        """
        Records a single observation to short-term memory.
        Fire-and-forget — errors are logged but not raised.
        """
        try:
            obs = Observation(
                user_id=user_id,
                observation_type=observation_type,
                data=data,
                task_id=task_id,
            )
            collection_path = f"{_COLLECTION}/{user_id}/{_SUBCOLLECTION}"
            self._set_document(collection_path, obs.id, obs.to_dict())

            logger.debug(
                "Observation recorded",
                user_id=user_id,
                type=observation_type,
                task_id=task_id,
            )
        except Exception as exc:
            # Short-term memory failure is non-fatal
            logger.warning(
                "Failed to record observation — continuing",
                user_id=user_id,
                type=observation_type,
                error=str(exc),
            )

    def get_recent(
        self,
        user_id: str,
        limit: int = 20,
        task_id: Optional[str] = None,
    ) -> list[dict]:
        """
        Retrieves recent observations for a user.
        Optionally filtered by task_id.
        """
        try:
            filters = []
            if task_id:
                filters.append(("taskId", "==", task_id))

            docs = self._subcollection_query(
                parent_collection=_COLLECTION,
                parent_id=user_id,
                subcollection=_SUBCOLLECTION,
                filters=filters if filters else None,
                order_by="createdAt",
                descending=True,
                limit=limit,
            )

            # Filter out expired observations
            now = datetime.now(timezone.utc).isoformat()
            return [d for d in docs if d.get("expiresAt", "") > now]

        except Exception as exc:
            logger.warning(
                "Failed to retrieve observations",
                user_id=user_id,
                error=str(exc),
            )
            return []

    def get_session_summary(self, user_id: str) -> dict:
        """
        Returns a structured summary of the current session.
        Used by MemoryAgent to build context.
        """
        observations = self.get_recent(user_id, limit=50)

        summary: dict = {
            "total_observations": len(observations),
            "tasks_in_focus": [],
            "recent_interventions": [],
            "milestones_completed_today": 0,
            "intervention_outcomes": {},
            "last_active_task_id": None,
            "session_start": None,
        }

        for obs in reversed(observations):  # chronological order
            obs_type = obs.get("type")
            data = obs.get("data", {})
            task_id = obs.get("taskId")

            if obs_type == OBS_SESSION_START and not summary["session_start"]:
                summary["session_start"] = obs.get("createdAt")

            elif obs_type == OBS_TASK_FOCUSED:
                if task_id and task_id not in summary["tasks_in_focus"]:
                    summary["tasks_in_focus"].append(task_id)
                summary["last_active_task_id"] = task_id

            elif obs_type == OBS_MILESTONE_COMPLETED:
                summary["milestones_completed_today"] += 1

            elif obs_type == OBS_INTERVENTION_FIRED:
                level = data.get("level", 0)
                summary["recent_interventions"].append(
                    {
                        "level": level,
                        "task_id": task_id,
                        "fired_at": obs.get("createdAt"),
                    }
                )

            elif obs_type == OBS_INTERVENTION_OUTCOME:
                outcome = data.get("outcome", "unknown")
                level = data.get("level", 0)
                key = f"level_{level}"
                if key not in summary["intervention_outcomes"]:
                    summary["intervention_outcomes"][key] = []
                summary["intervention_outcomes"][key].append(outcome)

        return summary

    def compress_for_prompt(self, user_id: str) -> str:
        """
        Returns a token-efficient string representation of recent session
        for injection into agent prompts.
        """
        summary = self.get_session_summary(user_id)

        if summary["total_observations"] == 0:
            return "No session activity recorded yet."

        parts = []

        if summary["milestones_completed_today"] > 0:
            parts.append(
                f"Milestones completed today: {summary['milestones_completed_today']}"
            )

        if summary["recent_interventions"]:
            recent = summary["recent_interventions"][-3:]
            levels = [str(i["level"]) for i in recent]
            parts.append(f"Recent interventions: Level {', '.join(levels)}")

        if summary["intervention_outcomes"]:
            for level_key, outcomes in summary["intervention_outcomes"].items():
                accepted = outcomes.count("accepted")
                dismissed = outcomes.count("dismissed")
                parts.append(
                    f"{level_key} outcomes: {accepted} accepted, {dismissed} dismissed"
                )

        if summary["tasks_in_focus"]:
            parts.append(
                f"Tasks worked on this session: {len(summary['tasks_in_focus'])}"
            )

        return " | ".join(parts) if parts else "Active session with no notable events."

    def clear_expired(self, user_id: str) -> int:
        """
        Removes expired observations for a user.
        Called by a daily Cloud Scheduler job.
        Returns count of deleted observations.
        """
        try:
            observations = self.get_recent(user_id, limit=100)
            now = datetime.now(timezone.utc).isoformat()
            expired = [
                o for o in observations if o.get("expiresAt", "") <= now
            ]

            collection_path = f"{_COLLECTION}/{user_id}/{_SUBCOLLECTION}"
            for obs in expired:
                self._delete_document(collection_path, obs["id"])

            logger.info(
                "Expired observations cleared",
                user_id=user_id,
                count=len(expired),
            )
            return len(expired)

        except Exception as exc:
            logger.warning(
                "Failed to clear expired observations",
                user_id=user_id,
                error=str(exc),
            )
            return 0