"""
SPARK — Agent Implementations Package
Import all agent modules to trigger @register_agent decorators.
All 10 SPARK agents are registered here.
"""

from app.agents.implementations import (
    memory_agent,
    context_agent,
    planner_agent,
    activation_agent,
    momentum_agent,
    risk_agent,
    simulation_agent,
    intervention_agent,
    recovery_agent,
    reflection_agent,
)

__all__ = [
    "memory_agent",
    "context_agent",
    "planner_agent",
    "activation_agent",
    "momentum_agent",
    "risk_agent",
    "simulation_agent",
    "intervention_agent",
    "recovery_agent",
    "reflection_agent",
]