"""
SPARK — CMS Calculation Tests
Verifies the mathematical CMS engine produces correct scores.
"""

import pytest
from datetime import datetime, timedelta, timezone
from app.models.task import Task
from app.services.cms_service import CMSService


@pytest.fixture
def cms_service():
    return CMSService()


def _make_task(
    progress: float = 0.0,
    hours_ago_created: float = 24.0,
    hours_until_deadline: float = 48.0,
    estimated_hours: float = 8.0,
) -> Task:
    """Helper to create a task with specific timing."""
    now = datetime.now(timezone.utc)
    created = (now - timedelta(hours=hours_ago_created)).isoformat()
    deadline = (now + timedelta(hours=hours_until_deadline)).isoformat()

    task = Task.create_new(
        user_id="test-user",
        title="Test Task",
        description="",
        category="work",
        priority="medium",
        deadline=deadline,
        estimated_hours=estimated_hours,
        complexity="medium",
    )
    task.createdAt = created
    task.progress.percentage = progress
    return task


class TestCMSCalculation:
    def test_new_task_has_moderate_score(self, cms_service):
        """A brand new task with lots of time should have a moderate score."""
        task = _make_task(progress=0, hours_until_deadline=168)
        result = cms_service.calculate_cms(task)
        assert 20 <= result.score <= 60

    def test_completed_task_has_high_score(self, cms_service):
        """A task at 100% progress should score near 100."""
        task = _make_task(progress=100, hours_until_deadline=48)
        result = cms_service.calculate_cms(task)
        assert result.score >= 80
        assert result.failure_risk <= 20

    def test_behind_schedule_has_low_score(self, cms_service):
        """A task with 10% progress and little time left should score low."""
        task = _make_task(
            progress=10,
            hours_ago_created=72,
            hours_until_deadline=4,
            estimated_hours=20,
        )
        result = cms_service.calculate_cms(task)
        assert result.score < 40
        assert result.failure_risk > 60

    def test_overdue_task_scores_zero_feasibility(self, cms_service):
        """A task past its deadline with incomplete progress."""
        task = _make_task(
            progress=30,
            hours_ago_created=100,
            hours_until_deadline=-2,
            estimated_hours=20,
        )
        result = cms_service.calculate_cms(task)
        assert result.failure_risk >= 50

    def test_ai_adjustment_affects_score(self, cms_service):
        """AI adjustment should shift the score within bounds."""
        task = _make_task(progress=50, hours_until_deadline=48)
        baseline = cms_service.calculate_cms(task, ai_adjustment=0.0)
        boosted = cms_service.calculate_cms(task, ai_adjustment=15.0)
        reduced = cms_service.calculate_cms(task, ai_adjustment=-15.0)

        assert boosted.score > baseline.score
        assert reduced.score < baseline.score
        assert 0 <= boosted.score <= 100
        assert 0 <= reduced.score <= 100

    def test_trend_detection(self, cms_service):
        """Score improvement should be detected as improving trend."""
        task = _make_task(progress=60, hours_until_deadline=72)
        task.cms.score = 30.0  # Previous low score
        result = cms_service.calculate_cms(task)
        assert result.trend == "improving"

    def test_score_always_bounded(self, cms_service):
        """CMS score must always be between 0 and 100."""
        for progress in [0, 25, 50, 75, 100]:
            for deadline_hours in [1, 12, 48, 168]:
                task = _make_task(
                    progress=progress,
                    hours_until_deadline=deadline_hours,
                )
                result = cms_service.calculate_cms(task)
                assert 0 <= result.score <= 100
                assert 0 <= result.failure_risk <= 100
                assert 0 <= result.completion_probability <= 1