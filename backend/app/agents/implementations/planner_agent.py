"""
SPARK — Planner Agent
Decomposes tasks into concrete, time-bounded milestones using Gemini.

Triggered: synchronously on task creation
Input: task details + genome context + calendar context
Output: ExecutionPlan with milestones and first action

The Planner Agent is the first agent that runs for every new task.
Its output determines the initial milestone structure that all
subsequent agents (Momentum, Risk, Intervention) work with.
"""

from app.agents.base_agent import BaseAgent
from app.agents.registry import register_agent
from app.ai.parsers.plan_parser import ExecutionPlan
from app.ai.prompts.planning_prompts import build_task_planning_prompt
from app.ai.prompts.system_prompts import get_planner_system_prompt
from app.models.agent import AgentContext, AgentResult


@register_agent
class PlannerAgent(BaseAgent):
    """
    Generates an AI-powered execution plan for a new task.
    Uses Gemini 2.5 Flash to decompose tasks into milestones.
    """

    name = "planner_agent"

    async def _execute(self, context: AgentContext) -> AgentResult:
        """
        Calls Gemini to generate a structured execution plan.
        Returns ExecutionPlan data as a dict.
        """
        if not context.task_id or not context.task_title:
            return AgentResult.failure_result(
                agent_name=self.name,
                error="PlannerAgent requires task_id and task_title in context",
            )

        gemini = self._get_gemini_client()

        # Build the planning prompt
        prompt = build_task_planning_prompt(
            task_title=context.task_title,
            task_description=context.task_description or "",
            deadline=context.task_deadline or "Not specified",
            estimated_hours=context.task_estimated_hours or 1.0,
            complexity=context.task_complexity or "medium",
            category=context.task_category or "personal",
            genome_context=context.genome_context,
        )

        # Call Gemini with structured output
        try:
            plan: ExecutionPlan = await gemini.generate_structured(
                prompt=prompt,
                response_model=ExecutionPlan,
                system_instruction=get_planner_system_prompt(),
                agent_role="planner",
                temperature=0.3,
            )
        except Exception as exc:
            return AgentResult.failure_result(
                agent_name=self.name,
                error=f"Gemini generation failed: {exc}",
            )

        self._logger.info(
            "Execution plan generated",
            task_id=context.task_id,
            milestone_count=len(plan.milestones),
            total_hours=plan.total_estimated_hours,
            first_action=plan.first_action[:60],
        )

        # Convert Pydantic model to dict for storage
        return AgentResult.success_result(
            agent_name=self.name,
            data={
                "milestones": [
                    {
                        "title": m.title,
                        "description": m.description,
                        "order": m.order,
                        "estimated_minutes": m.estimated_minutes,
                        "is_first_action": m.is_first_action,
                    }
                    for m in plan.milestones
                ],
                "total_estimated_hours": plan.total_estimated_hours,
                "first_action": plan.first_action,
                "implicit_requirements": plan.implicit_requirements,
                "confidence": plan.confidence,
            },
        )