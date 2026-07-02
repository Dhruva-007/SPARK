"""
SPARK — Context Agent
Gathers comprehensive context about the user's current situation.

Provides:
- Current time and working hours status
- Active task count and workload assessment
- Calendar availability (Phase 8+: real Google Calendar)
- Cognitive load estimation based on task count

The ContextAgent is called by the Orchestrator's build_context()
and its output is injected into AgentContext for all other agents.
"""

from datetime import datetime, timezone

from app.agents.base_agent import BaseAgent
from app.agents.registry import register_agent
from app.models.agent import AgentContext, AgentResult


@register_agent
class ContextAgent(BaseAgent):
    """
    Gathers and structures context for other agents.
    Does not call Gemini — pure data aggregation.
    """

    name = "context_agent"

    async def _execute(self, context: AgentContext) -> AgentResult:
        """
        Assembles a context snapshot from available data.
        Returns a structured dict that enriches AgentContext.
        """
        now = datetime.now(timezone.utc)

        # Determine if user is in working hours
        try:
            start_h, start_m = map(int, context.working_hours_start.split(":"))
            end_h, end_m = map(int, context.working_hours_end.split(":"))
            current_h = now.hour
            current_m = now.minute

            start_minutes = start_h * 60 + start_m
            end_minutes = end_h * 60 + end_m
            current_minutes = current_h * 60 + current_m

            in_working_hours = start_minutes <= current_minutes <= end_minutes
        except Exception:
            in_working_hours = True  # Default: assume yes

        # Cognitive load assessment
        task_count = context.active_task_count
        if task_count == 0:
            cognitive_load = "none"
        elif task_count <= 2:
            cognitive_load = "low"
        elif task_count <= 4:
            cognitive_load = "moderate"
        elif task_count <= 6:
            cognitive_load = "high"
        else:
            cognitive_load = "overloaded"

        # Time of day category
        hour = now.hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"

        context_snapshot = {
            "current_time_iso": now.isoformat(),
            "in_working_hours": in_working_hours,
            "time_of_day": time_of_day,
            "day_of_week": now.strftime("%A"),
            "active_task_count": task_count,
            "active_task_titles": context.active_task_titles,
            "cognitive_load": cognitive_load,
            "calendar_events": [],  # Phase 8+: real Google Calendar
            "genome_context": context.genome_context,
        }

        return AgentResult.success_result(
            agent_name=self.name,
            data=context_snapshot,
        )