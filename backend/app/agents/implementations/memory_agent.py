"""
SPARK — Memory Agent
Assembles rich context from both short-term and long-term memory.

The MemoryAgent is called by the Orchestrator before every other agent.
It enriches the AgentContext with:
- Compressed long-term behavioral context (genome)
- Session observations (short-term memory)
- Behavioral summary for the current moment
- Intervention history awareness

This ensures every agent decision is informed by both
persistent behavioral patterns and recent session activity.
"""

from datetime import datetime, timezone

from app.agents.base_agent import BaseAgent
from app.agents.registry import register_agent
from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory
from app.models.agent import AgentContext, AgentResult


@register_agent
class MemoryAgent(BaseAgent):
    """
    Assembles memory context for other agents.
    Always runs first in multi-agent workflows.
    """

    name = "memory_agent"

    def __init__(self) -> None:
        super().__init__()
        self._stm = ShortTermMemory()
        self._ltm = LongTermMemory()

    async def _execute(self, context: AgentContext) -> AgentResult:
        """
        Reads from both memory layers and returns an enriched context dict.
        """
        user_id = context.user_id

        # ── Long-term memory (Genome) ──────────────────────
        try:
            behavioral_summary = self._ltm.get_behavioral_summary(user_id)
            ltm_context = self._ltm.compress_for_prompt(user_id)
        except Exception as exc:
            self._logger.warning(
                "Long-term memory read failed — using defaults",
                error=str(exc),
            )
            behavioral_summary = {}
            ltm_context = "No behavioral history available yet"

        # ── Short-term memory (Session) ────────────────────
        try:
            stm_context = self._stm.compress_for_prompt(user_id)
            session_summary = self._stm.get_session_summary(user_id)
        except Exception as exc:
            self._logger.warning(
                "Short-term memory read failed — using defaults",
                error=str(exc),
            )
            stm_context = "No session activity recorded"
            session_summary = {}

        # ── Compose enriched genome context for prompt injection ──
        enriched_context = _compose_memory_context(
            ltm_context=ltm_context,
            stm_context=stm_context,
            behavioral_summary=behavioral_summary,
        )

        # ── Record this memory access as an observation ────
        try:
            from app.memory.short_term import OBS_AGENT_RUN
            self._stm.record(
                user_id=user_id,
                observation_type=OBS_AGENT_RUN,
                data={
                    "agent": "memory_agent",
                    "task_id": context.task_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
        except Exception:
            pass  # Memory recording is non-fatal

        return AgentResult.success_result(
            agent_name=self.name,
            data={
                "enriched_genome_context": enriched_context,
                "behavioral_summary": behavioral_summary,
                "session_summary": session_summary,
                "ltm_context": ltm_context,
                "stm_context": stm_context,
                "is_peak_hour": behavioral_summary.get("is_peak_hour", False),
                "preferred_intervention_level": behavioral_summary.get(
                    "preferred_intervention_level", 2
                ),
            },
        )


def _compose_memory_context(
    ltm_context: str,
    stm_context: str,
    behavioral_summary: dict,
) -> str:
    """
    Composes a single compressed context string from both memory layers.
    Target: under 200 tokens total.
    Injected into every agent prompt as genome_context.
    """
    parts = [f"Behavioral profile: {ltm_context}"]

    is_peak = behavioral_summary.get("is_peak_hour", False)
    current_hour = behavioral_summary.get("current_hour", 12)
    focus_duration = behavioral_summary.get("focus_duration_minutes", 45)

    if is_peak:
        parts.append(f"Currently in peak productivity window (hour {current_hour})")
    else:
        parts.append(
            f"Outside peak hours (hour {current_hour}) — "
            f"suggest shorter {min(focus_duration, 25)}min sessions"
        )

    if stm_context and stm_context != "No session activity recorded yet.":
        parts.append(f"Session: {stm_context}")

    preferred_level = behavioral_summary.get("preferred_intervention_level", 2)
    parts.append(f"Best intervention level: {preferred_level}")

    return " | ".join(parts)