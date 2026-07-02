"""
SPARK — Base Agent
Abstract base class that all SPARK agents inherit from.

Every agent has:
- A unique name
- A single run() method that takes AgentContext and returns AgentResult
- Built-in timing and error handling
- Access to GeminiClient and GenomeService via the base class
- Structured logging with agent context

Design principles:
- Agents are stateless — all state comes from AgentContext
- Agents never write to Firestore directly — they return data
- Repositories and services are called by orchestrator or TaskService
- Every agent failure returns AgentResult.failure_result() — never raises
"""

import time
from abc import ABC, abstractmethod
from typing import Optional

from app.core.logging import get_logger
from app.models.agent import AgentContext, AgentResult

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all SPARK agents.

    Subclasses must implement:
        name: str class attribute
        _execute(context: AgentContext) -> AgentResult

    The run() method wraps _execute with timing, logging, and error handling.
    """

    name: str = "base_agent"

    def __init__(self) -> None:
        self._logger = get_logger(f"agents.{self.name}")

    async def run(self, context: AgentContext) -> AgentResult:
        """
        Public entry point for every agent.
        Wraps _execute with timing, logging, and safe error handling.
        Never raises — always returns an AgentResult.
        """
        start_time = time.perf_counter()

        self._logger.info(
            "Agent started",
            agent=self.name,
            user_id=context.user_id,
            task_id=context.task_id,
        )

        try:
            result = await self._execute(context)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            result.execution_time_ms = elapsed_ms

            if result.success:
                self._logger.info(
                    "Agent completed successfully",
                    agent=self.name,
                    duration_ms=elapsed_ms,
                )
            else:
                self._logger.warning(
                    "Agent completed with failure",
                    agent=self.name,
                    error=result.error,
                    duration_ms=elapsed_ms,
                )

            return result

        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            self._logger.error(
                "Agent raised unhandled exception",
                agent=self.name,
                error=str(exc),
                duration_ms=elapsed_ms,
                exc_info=True,
            )
            return AgentResult.failure_result(
                agent_name=self.name,
                error=f"Unhandled exception: {exc}",
            )

    @abstractmethod
    async def _execute(self, context: AgentContext) -> AgentResult:
        """
        Core agent logic. Implemented by each subclass.
        Must return AgentResult — never raise.
        """
        ...

    def _get_gemini_client(self):
        """Returns the shared GeminiClient singleton."""
        from app.ai.gemini_client import get_gemini_client
        return get_gemini_client()

    def _get_genome_service(self):
        """Returns a GenomeService instance."""
        from app.services.genome_service import GenomeService
        return GenomeService()