"""
SPARK — Health Endpoint Tests
Verifies liveness and readiness probes work correctly.
"""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_returns_ok(client):
    """Liveness probe returns 200 with status ok."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data
    assert "uptime_seconds" in data


def test_readiness_returns_checks(client):
    """Readiness probe returns check details."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "checks" in data
    assert data["checks"]["api"] == "ok"
    assert data["checks"]["config"] == "ok"