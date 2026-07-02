"""
SPARK — Agent Registry
Maintains a catalog of all registered agents.
Agents register themselves by name for discovery by the orchestrator.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.agents.base_agent import BaseAgent

from app.core.logging import get_logger

logger = get_logger(__name__)

# Registry: agent_name → agent class (not instance)
_registry: dict[str, type] = {}


def register_agent(agent_class: type) -> type:
    """
    Decorator that registers an agent class in the registry.

    Usage:
        @register_agent
        class PlannerAgent(BaseAgent):
            name = "planner_agent"
            ...
    """
    name = getattr(agent_class, "name", None)
    if not name:
        raise ValueError(f"Agent class {agent_class.__name__} must define a 'name' attribute")

    _registry[name] = agent_class
    logger.debug("Agent registered", agent_name=name)
    return agent_class


def get_agent(name: str) -> "BaseAgent":
    """
    Returns a new instance of the named agent.
    Raises KeyError if the agent is not registered.
    """
    if name not in _registry:
        raise KeyError(f"Agent '{name}' is not registered. Available: {list(_registry.keys())}")
    return _registry[name]()


def list_agents() -> list[str]:
    """Returns the names of all registered agents."""
    return list(_registry.keys())


def is_registered(name: str) -> bool:
    """Returns True if an agent with the given name is registered."""
    return name in _registry