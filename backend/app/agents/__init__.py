"""
SPARK — Agent Framework Package
Importing this package registers all agents automatically.
"""

# Import implementations to trigger registration
import app.agents.implementations  # noqa: F401

from app.agents.base_agent import BaseAgent
from app.agents.orchestrator import AgentOrchestrator
from app.agents.registry import get_agent, list_agents, is_registered

__all__ = [
    "BaseAgent",
    "AgentOrchestrator",
    "get_agent",
    "list_agents",
    "is_registered",
]