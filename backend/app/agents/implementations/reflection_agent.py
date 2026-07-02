"""
SPARK — Reflection Agent
Post-task analysis that updates the Completion Genome.

Triggered after a task is completed or failed.
Analyzes what happened and extracts behavioral updates.
"""

from app.agents.base_agent import BaseAgent
from app.agents.registry import register_agent
from app.ai.parsers.intervention_parser import ReflectionResponse
from app.ai.prompts.reflection_prompts import build_reflection_prompt
from app.ai.prompts.system_prompts import get_reflection_system_prompt
from app.models.agent import AgentContext, AgentResult


@register_agent
class ReflectionAgent(BaseAgent):
    """Analyzes completed tasks and generates genome updates."""

    name = "reflection_agent"

    async def _execute(self, context: AgentContext) -> AgentResult:
        if not context.task_id or not context.task_title:
            return AgentResult.failure_result(
                agent_name=self.name,
                error="ReflectionAgent requires task_id and task_title",
            )

        gemini = self._get_gemini_client()

        # Get task and intervention data from context extras
        completion_status = context.extra.get("completion_status", "on_time")
        deadline = context.task_deadline or ""
        completed_at = context.extra.get("completed_at")
        estimated_hours = context.task_estimated_hours or 1.0
        actual_hours = context.extra.get("actual_hours", estimated_hours)
        interventions_used = context.extra.get("interventions_used", [])
        milestones_completed = context.extra.get("milestones_completed", 0)
        milestones_total = context.extra.get("milestones_total", 0)

        # Get current genome for context
        try:
            from app.services.genome_service import GenomeService
            genome_service = GenomeService()
            genome = genome_service.get_genome(context.user_id)
            current_genome = genome.model_dump()
        except Exception:
            current_genome = {}

        prompt = build_reflection_prompt(
            task_title=context.task_title,
            completion_status=completion_status,
            deadline=deadline,
            completed_at=completed_at,
            estimated_hours=estimated_hours,
            actual_hours=actual_hours,
            interventions_used=interventions_used,
            milestones_completed=milestones_completed,
            milestones_total=milestones_total,
            current_genome=current_genome,
        )

        try:
            reflection: ReflectionResponse = await gemini.generate_structured(
                prompt=prompt,
                response_model=ReflectionResponse,
                system_instruction=get_reflection_system_prompt(),
                agent_role="reflection",
                temperature=0.4,
            )
        except Exception as exc:
            self._logger.warning(
                "AI reflection failed — using basic analysis",
                error=str(exc),
            )
            return AgentResult.success_result(
                agent_name=self.name,
                data={
                    "what_worked": ["Task was completed"],
                    "what_caused_delays": ["No AI analysis available"],
                    "effective_interventions": [],
                    "genome_updates": {},
                    "behavioral_summary": (
                        f"Task '{context.task_title}' was completed {completion_status}."
                    ),
                },
            )

        self._logger.info(
            "Reflection analysis complete",
            task_id=context.task_id,
            genome_update_keys=list(reflection.genome_updates.keys()),
        )

        # Apply genome updates
        try:
            from app.memory.long_term import LongTermMemory
            ltm = LongTermMemory()

            ltm.record_estimation_result(
                user_id=context.user_id,
                estimated_hours=estimated_hours,
                actual_hours=actual_hours,
                complexity=context.task_complexity or "medium",
            )
        except Exception as exc:
            self._logger.warning(
                "Genome estimation update failed",
                error=str(exc),
            )

        return AgentResult.success_result(
            agent_name=self.name,
            data={
                "what_worked": reflection.what_worked,
                "what_caused_delays": reflection.what_caused_delays,
                "effective_interventions": reflection.effective_interventions,
                "genome_updates": reflection.genome_updates,
                "behavioral_summary": reflection.behavioral_summary,
            },
        )