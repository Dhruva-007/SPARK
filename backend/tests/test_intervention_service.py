"""
SPARK — Intervention Service Tests
Verifies intervention level determination and anti-fatigue logic.
"""

import pytest
from app.services.intervention_service import InterventionService


@pytest.fixture
def service():
    return InterventionService()


class TestInterventionLevels:
    def test_low_risk_is_level_0(self, service):
        assert service.determine_level(10) == 0
        assert service.determine_level(29) == 0

    def test_moderate_risk_is_level_1(self, service):
        assert service.determine_level(30) == 1
        assert service.determine_level(49) == 1

    def test_medium_risk_is_level_2(self, service):
        assert service.determine_level(50) == 2
        assert service.determine_level(64) == 2

    def test_high_risk_is_level_3(self, service):
        assert service.determine_level(65) == 3
        assert service.determine_level(79) == 3

    def test_critical_risk_is_level_4(self, service):
        assert service.determine_level(80) == 4
        assert service.determine_level(89) == 4

    def test_extreme_risk_is_level_5(self, service):
        assert service.determine_level(90) == 5
        assert service.determine_level(100) == 5

    def test_intervention_type_mapping(self, service):
        assert service.get_intervention_type(0) == "suggestion"
        assert service.get_intervention_type(1) == "suggestion"
        assert service.get_intervention_type(2) == "momentum"
        assert service.get_intervention_type(3) == "collaboration"
        assert service.get_intervention_type(4) == "critical"
        assert service.get_intervention_type(5) == "recovery"