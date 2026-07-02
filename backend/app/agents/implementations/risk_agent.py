"""
SPARK — Risk Prediction Agent
Calculates precise failure probability using Gemini analysis
combined with mathematical feasibility metrics.

Triggered:
- Every 15 minutes by CMS worker
- After any task progress update
- When PONR is recalculated

Output:
- Failure probability (0.0-1.0)
- Primary risk factor
- PONR timestamp
- Recommended intervention level
- Immediate action to reduce risk
"""

from app.agents.base_agent import BaseAgent
from app.agents.registry import register_agent
from app.ai.parsers.intervention_parser import RiskAssessmentResponse
from app.ai.prompts.risk_prompts import build_risk_assessment_prompt
from app.ai.prompts.system_prompts import get_risk_system_prompt
from app.models.agent import AgentContext, AgentResult


@register_agent
class RiskAgent(BaseAgent):
    """Predicts failure probability for tasks using AI + math."""

    name = "risk_agent"

    async def _execute(self, context: AgentContext) -> AgentResult:
        if not context.task_id or not context.task_title:
            return AgentResult.failure_result(
                agent_name=self.name,
                error="RiskAgent requires task_id and task_title in context",
            )

        gemini = self._get_gemini_client()

        progress = context.task_progress or 0.0
        estimated_hours = context.task_estimated_hours or 1.0
        remaining_hours = estimated_hours * (1 - progress / 100)
        hours_until_deadline = context.extra.get("hours_until_deadline", 24.0)
        available_productive = context.extra.get("available_productive_hours", 8.0)

        prompt = build_risk_assessment_prompt(
            task_title=context.task_title,
            progress_percentage=progress,
            hours_until_deadline=hours_until_deadline,
            estimated_remaining_hours=remaining_hours,
            available_productive_hours=available_productive,
            active_task_count=context.active_task_count,
            genome_context=context.genome_context,
        )

        try:
            assessment: RiskAssessmentResponse = await gemini.generate_structured(
                prompt=prompt,
                response_model=RiskAssessmentResponse,
                system_instruction=get_risk_system_prompt(),
                agent_role="risk",
                temperature=0.2,
            )
        except Exception as exc:
            # Graceful degradation — calculate risk mathematically
            self._logger.warning(
                "AI risk assessment failed — using math fallback",
                error=str(exc),
            )
            if hours_until_deadline <= 0:
                math_risk = 1.0 if progress < 100 else 0.0
            elif remaining_hours <= 0:
                math_risk = 0.0
            else:
                feasibility = hours_until_deadline / max(remaining_hours, 0.1)
                math_risk = max(0.0, min(1.0, 1.0 - (feasibility / 2)))

            return AgentResult.success_result(
                agent_name=self.name,
                data={
                    "failure_probability": round(math_risk, 3),
                    "primary_risk_factor": "Mathematical feasibility estimate",
                    "ponr_timestamp": None,
                    "recommended_intervention_level": (
                        0 if math_risk < 0.3 else
                        1 if math_risk < 0.5 else
                        2 if math_risk < 0.65 else
                        3 if math_risk < 0.8 else
                        4 if math_risk < 0.9 else 5
                    ),
                    "immediate_action": "Continue working on the current milestone",
                    "source": "mathematical_fallback",
                },
            )

        self._logger.info(
            "Risk assessment complete",
            task_id=context.task_id,
            failure_probability=assessment.failure_probability,
            recommended_level=assessment.recommended_intervention_level,
        )

        return AgentResult.success_result(
            agent_name=self.name,
            data={
                "failure_probability": assessment.failure_probability,
                "primary_risk_factor": assessment.primary_risk_factor,
                "ponr_timestamp": assessment.ponr_timestamp,
                "recommended_intervention_level": assessment.recommended_intervention_level,
                "immediate_action": assessment.immediate_action,
                "source": "ai_assessment",
            },
        )