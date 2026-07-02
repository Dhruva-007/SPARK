"""
SPARK — Analytics Service
Aggregates completion health data and risk matrices.
"""

from app.core.logging import get_logger
from app.repositories.analytics_repository import AnalyticsRepository

logger = get_logger(__name__)


class AnalyticsService:
    """Provides completion analytics and insights."""

    def __init__(self) -> None:
        self._analytics_repo = AnalyticsRepository()

    def get_completion_health(self, user_id: str) -> dict:
        """Returns the overall completion health score and metrics."""
        return self._analytics_repo.get_completion_health(user_id)

    def get_risk_matrix(self, user_id: str) -> list[dict]:
        """Returns all active tasks with risk data for visualization."""
        return self._analytics_repo.get_risk_matrix(user_id)