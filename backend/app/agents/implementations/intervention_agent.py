"""
SPARK — Intervention Agent
Generates contextual, level-appropriate intervention messages.

Uses Gemini to craft messages that match the urgency level:
- Level 1: Warm, encouraging nudge
- Level 2: Momentum micro-steps
- Level 3: Active collaboration
- Level 4: Urgent restructuring
- Level 5: Damage control

The message tone is calibrated to the user's communication style
preference from their Completion Genome.
"""

from app.agents.base_agent import BaseAgent
from app.agents.registry import register_agent
from app.ai.parsers.intervention_parser import InterventionResponse
from app.ai.prompts.intervention_prompts import build_intervention_prompt
from app.ai.prompts.system_prompts import get_intervention_system_prompt
from app.models.agent import AgentContext, AgentResult


@register_agent
class InterventionAgent(BaseAgent):
    """Generates AI-powered intervention messages calibrated to risk level."""

    name = "intervention_agent"

    async def _execute(self, context: AgentContext) -> AgentResult:
        if not context.task_id or not context.task_title:
            return AgentResult.failure_result(
                agent_name=self.name,
                error="InterventionAgent requires task_id and task_title",
            )

        gemini = self._get_gemini_client()

        level = context.extra.get("intervention_level", 2)
        failure_risk = context.extra.get("failure_risk", 50.0)
        cms_score = context.extra.get("cms_score", 50.0)
        hours_until_deadline = context.extra.get("hours_until_deadline", 24.0)
        hours_until_ponr = context.extra.get("hours_until_ponr")
        next_milestone = context.extra.get("next_milestone")

        prompt = build_intervention_prompt(
            task_title=context.task_title,
            intervention_level=level,
            failure_risk=failure_risk / 100,
            cms_score=cms_score,
            hours_until_deadline=hours_until_deadline,
            hours_until_ponr=hours_until_ponr,
            next_milestone=next_milestone,
            genome_context=context.genome_context,
        )

        try:
            response: InterventionResponse = await gemini.generate_structured(
                prompt=prompt,
                response_model=InterventionResponse,
                system_instruction=get_intervention_system_prompt(),
                agent_role="intervention",
                temperature=0.5,
            )
        except Exception as exc:
            self._logger.warning(
                "AI intervention generation failed — using template",
                error=str(exc),
            )
            return AgentResult.success_result(
                agent_name=self.name,
                data=self._fallback_intervention(
                    context.task_title, level, failure_risk
                ),
            )

        self._logger.info(
            "Intervention generated",
            task_id=context.task_id,
            level=level,
            action=response.next_action[:60],
        )

        return AgentResult.success_result(
            agent_name=self.name,
            data={
                "level": level,
                "message": response.message,
                "next_action": response.next_action,
                "estimated_minutes": response.estimated_minutes,
                "rationale": response.rationale,
            },
        )

    def _fallback_intervention(
        self, task_title: str, level: int, failure_risk: float
    ) -> dict:
        """Template-based fallback when AI is unavailable."""
        templates = {
            1: {
                "message": f'"{task_title}" could use some attention today.',
                "next_action": "Open the task and review your progress so far.",
                "estimated_minutes": 10,
            },
            2: {
                "message": f'"{task_title}" needs momentum. Break it into a small action.',
                "next_action": "Complete the next milestone in a 25-minute focused session.",
                "estimated_minutes": 25,
            },
            3: {
                "message": f'Let\'s work on "{task_title}" together right now.',
                "next_action": "Start the current milestone and work for 30 minutes.",
                "estimated_minutes": 30,
            },
            4: {
                "message": f'URGENT: "{task_title}" is at {failure_risk:.0f}% failure risk.',
                "next_action": "Drop everything and work on this task for the next hour.",
                "estimated_minutes": 60,
            },
            5: {
                "message": f'CRITICAL: "{task_title}" needs damage control immediately.',
                "next_action": "Assess what can be delivered and draft an extension request.",
                "estimated_minutes": 45,
            },
        }

        template = templates.get(level, templates[2])
        return {
            "level": level,
            "message": template["message"],
            "next_action": template["next_action"],
            "estimated_minutes": template["estimated_minutes"],
            "rationale": "Template-based intervention (AI unavailable)",
        }