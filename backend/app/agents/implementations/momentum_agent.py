"""
SPARK — Momentum Agent
Identifies the next best action and provides CMS score adjustments.

Triggered:
- Every 15 minutes by Cloud Scheduler (CMS worker)
- When user requests the next action
- After a milestone is completed

Output:
- NextActionResponse: the single best next action
- CMSAdjustmentResponse: qualitative CMS modifier
"""

from app.agents.base_agent import BaseAgent
from app.agents.registry import register_agent
from app.ai.parsers.milestone_parser import NextActionResponse, CMSAdjustmentResponse
from app.ai.prompts.momentum_prompts import (
    build_next_action_prompt,
    build_cms_calculation_prompt,
)
from app.ai.prompts.system_prompts import get_momentum_system_prompt
from app.models.agent import AgentContext, AgentResult


@register_agent
class MomentumAgent(BaseAgent):
    """
    Maintains task momentum by identifying the next best action
    and providing qualitative CMS score adjustments.
    """

    name = "momentum_agent"

    async def _execute(self, context: AgentContext) -> AgentResult:
        """
        Generates the next best action and CMS adjustment.
        """
        if not context.task_id:
            return AgentResult.failure_result(
                agent_name=self.name,
                error="MomentumAgent requires task_id in context",
            )

        gemini = self._get_gemini_client()

        # Extract task-specific data from context
        progress = context.task_progress or 0.0
        deadline = context.task_deadline or ""
        estimated_hours = context.task_estimated_hours or 1.0
        cms_score = context.extra.get("cms_score", 50.0)
        hours_until_deadline = context.extra.get("hours_until_deadline", 24.0)
        last_milestone = context.extra.get("last_milestone_completed")
        next_milestone = context.extra.get("next_milestone")

        # Get next best action
        next_action_prompt = build_next_action_prompt(
            task_title=context.task_title or "Unknown task",
            current_progress=progress,
            last_milestone_completed=last_milestone,
            next_milestone=next_milestone,
            hours_until_deadline=hours_until_deadline,
            cms_score=cms_score,
            genome_context=context.genome_context,
        )

        try:
            next_action: NextActionResponse = await gemini.generate_structured(
                prompt=next_action_prompt,
                response_model=NextActionResponse,
                system_instruction=get_momentum_system_prompt(),
                agent_role="momentum",
                temperature=0.4,
            )
        except Exception as exc:
            return AgentResult.failure_result(
                agent_name=self.name,
                error=f"Next action generation failed: {exc}",
            )

        # Get CMS adjustment
        hours_elapsed = context.extra.get("hours_elapsed", 1.0)
        milestones_completed = context.extra.get("milestones_completed", 0)
        milestones_total = context.extra.get("milestones_total", 1)

        cms_prompt = build_cms_calculation_prompt(
            task_title=context.task_title or "Unknown task",
            progress_percentage=progress,
            hours_elapsed=hours_elapsed,
            hours_until_deadline=hours_until_deadline,
            estimated_total_hours=estimated_hours,
            milestones_completed=milestones_completed,
            milestones_total=milestones_total,
            genome_context=context.genome_context,
        )

        try:
            cms_adjustment: CMSAdjustmentResponse = await gemini.generate_structured(
                prompt=cms_prompt,
                response_model=CMSAdjustmentResponse,
                system_instruction=get_momentum_system_prompt(),
                agent_role="momentum",
                temperature=0.2,
            )
        except Exception as exc:
            self._logger.warning(
                "CMS adjustment generation failed — using defaults",
                error=str(exc),
            )
            # Graceful degradation — use no adjustment
            from app.ai.parsers.milestone_parser import CMSAdjustmentResponse
            cms_adjustment = CMSAdjustmentResponse(
                score_adjustment=0.0,
                primary_factor="Unable to calculate behavioral adjustment",
                failure_risk=max(0, 100 - cms_score),
                trend="stable",
            )

        self._logger.info(
            "Momentum analysis complete",
            task_id=context.task_id,
            next_action=next_action.action[:60],
            cms_adjustment=cms_adjustment.score_adjustment,
            trend=cms_adjustment.trend,
        )

        return AgentResult.success_result(
            agent_name=self.name,
            data={
                "next_action": next_action.action,
                "next_action_minutes": next_action.estimated_minutes,
                "next_action_rationale": next_action.rationale,
                "milestone_id": next_action.milestone_id,
                "cms_adjustment": cms_adjustment.score_adjustment,
                "failure_risk": cms_adjustment.failure_risk,
                "primary_factor": cms_adjustment.primary_factor,
                "trend": cms_adjustment.trend,
            },
        )