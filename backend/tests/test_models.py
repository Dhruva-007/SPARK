"""
SPARK — Model Validation Tests
Verifies Pydantic models accept valid data and reject invalid data.
"""

import pytest
from app.models.task import Task, CreateTaskRequest
from app.models.genome import CompletionGenome
from app.models.milestone import Milestone
from app.models.intervention import Intervention


class TestCreateTaskRequest:
    def test_valid_request(self):
        req = CreateTaskRequest(
            title="Test Task",
            description="A test task",
            category="work",
            priority="high",
            deadline="2026-12-31T23:59:59Z",
            estimatedHours=8.0,
            complexity="medium",
            tags=["test"],
        )
        assert req.title == "Test Task"
        assert req.estimatedHours == 8.0

    def test_empty_title_rejected(self):
        with pytest.raises(Exception):
            CreateTaskRequest(
                title="",
                deadline="2026-12-31T23:59:59Z",
                estimatedHours=8.0,
            )

    def test_negative_hours_rejected(self):
        with pytest.raises(Exception):
            CreateTaskRequest(
                title="Test",
                deadline="2026-12-31T23:59:59Z",
                estimatedHours=-1.0,
            )


class TestTask:
    def test_create_new(self):
        task = Task.create_new(
            user_id="user-001",
            title="Test Task",
            description="Description",
            category="academic",
            priority="high",
            deadline="2026-12-31T23:59:59Z",
            estimated_hours=10.0,
            complexity="high",
        )
        assert task.userId == "user-001"
        assert task.title == "Test Task"
        assert task.status == "pending"
        assert task.progress.percentage == 0.0
        assert task.cms.score == 0.0
        assert task.id  # UUID generated

    def test_to_firestore(self):
        task = Task.create_new(
            user_id="user-001",
            title="Test",
            description="",
            category="work",
            priority="medium",
            deadline="2026-12-31T23:59:59Z",
            estimated_hours=4.0,
            complexity="low",
        )
        data = task.to_firestore()
        assert isinstance(data, dict)
        assert data["userId"] == "user-001"
        assert data["title"] == "Test"
        assert "progress" in data
        assert "cms" in data


class TestCompletionGenome:
    def test_create_default(self):
        genome = CompletionGenome.create_default()
        assert genome.version == 1
        assert genome.productivity.peakHours == [9, 10, 14, 15]
        assert genome.completion.successRate == 0.7
        assert genome.estimation.averageUnderestimationFactor == 1.3

    def test_compressed_context(self):
        genome = CompletionGenome.create_default()
        context = genome.to_compressed_context()
        assert isinstance(context, str)
        assert "Peak hours" in context
        assert "Success rate" in context
        assert len(context) < 500  # Must be token-efficient

    def test_to_firestore(self):
        genome = CompletionGenome.create_default()
        data = genome.to_firestore()
        assert isinstance(data, dict)
        assert "productivity" in data
        assert "estimation" in data


class TestMilestone:
    def test_create(self):
        ms = Milestone(
            taskId="task-001",
            title="Write introduction",
            order=1,
            estimatedMinutes=30,
        )
        assert ms.taskId == "task-001"
        assert ms.status == "pending"
        assert ms.isNextAction is False


class TestIntervention:
    def test_create(self):
        iv = Intervention(
            taskId="task-001",
            userId="user-001",
            level=2,
            type="momentum",
            trigger="risk_threshold",
            message="Test message",
        )
        assert iv.level == 2
        assert iv.outcome is None