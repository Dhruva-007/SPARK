"""
SPARK — Analytics Repository
Aggregate queries for completion analytics.
Currently uses Firestore for basic aggregates.
BigQuery integration added in Phase 17 for advanced analytics.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.logging import get_logger
from app.repositories.base_repository import BaseRepository

logger = get_logger(__name__)


class AnalyticsRepository(BaseRepository):
    """Repository for analytics and aggregate queries."""

    def get_completion_health(self, user_id: str) -> dict:
        """
        Calculates the overall completion health score for a user.
        Aggregates data from active tasks.
        """
        try:
            # Get all tasks for user
            all_docs = self._query_collection(
                "tasks",
                filters=[("userId", "==", user_id)],
            )

            active_statuses = {"pending", "active", "in_progress"}
            active_tasks = [
                d for d in all_docs if d.get("status") in active_statuses
            ]
            completed_tasks = [
                d for d in all_docs if d.get("status") == "completed"
            ]

            # Calculate at-risk tasks (failure risk > 65%)
            at_risk = [
                t for t in active_tasks
                if (t.get("cms") or {}).get("failureRisk", 0) > 65
            ]

            # 7-day completion rate
            seven_days_ago = (
                datetime.now(timezone.utc) - timedelta(days=7)
            ).isoformat()
            recent_completed = [
                t for t in completed_tasks
                if (t.get("completedAt") or "") >= seven_days_ago
            ]
            recent_attempted = [
                t for t in all_docs
                if (t.get("createdAt") or "") >= seven_days_ago
                and t.get("status") in {"completed", "failed", "bankrupt"}
            ]
            completion_rate_7d = (
                len(recent_completed) / max(len(recent_attempted), 1)
            )

            # Average momentum across active tasks
            cms_scores = [
                (t.get("cms") or {}).get("score", 0) for t in active_tasks
            ]
            avg_momentum = (
                sum(cms_scores) / len(cms_scores) if cms_scores else 0
            )

            # Overall health score: weighted combination
            completion_weight = 0.4
            momentum_weight = 0.3
            risk_weight = 0.3

            risk_score = max(
                0,
                100 - (len(at_risk) / max(len(active_tasks), 1)) * 100,
            )

            health_score = (
                completion_rate_7d * 100 * completion_weight
                + avg_momentum * momentum_weight
                + risk_score * risk_weight
            )

            return {
                "healthScore": round(health_score, 1),
                "activeTasks": len(active_tasks),
                "atRiskTasks": len(at_risk),
                "completionRate7d": round(completion_rate_7d, 3),
                "avgMomentum": round(avg_momentum, 1),
            }

        except Exception as exc:
            logger.error(
                "Completion health calculation failed",
                user_id=user_id,
                error=str(exc),
            )
            return {
                "healthScore": 0,
                "activeTasks": 0,
                "atRiskTasks": 0,
                "completionRate7d": 0,
                "avgMomentum": 0,
            }

    def get_risk_matrix(self, user_id: str) -> list[dict]:
        """
        Returns all active tasks with their risk data for the risk matrix view.
        """
        docs = self._query_collection(
            "tasks",
            filters=[("userId", "==", user_id)],
            order_by="deadline",
            descending=False,
        )

        active_statuses = {"pending", "active", "in_progress"}
        risk_matrix = []

        for doc in docs:
            if doc.get("status") not in active_statuses:
                continue

            cms = doc.get("cms") or {}
            failure_risk = cms.get("failureRisk", 0)

            if failure_risk >= 80:
                risk_level = "critical"
            elif failure_risk >= 60:
                risk_level = "high"
            elif failure_risk >= 40:
                risk_level = "medium"
            else:
                risk_level = "low"

            risk_matrix.append(
                {
                    "taskId": doc.get("id"),
                    "title": doc.get("title"),
                    "failureRisk": failure_risk,
                    "momentum": cms.get("score", 0),
                    "deadline": doc.get("deadline"),
                    "riskLevel": risk_level,
                    "status": doc.get("status"),
                }
            )

        return risk_matrix