"""
SPARK — Recovery Agent
Activated when a task passes its Point of No Return.

Creates damage mitigation plans:
1. Extension email drafts (ready to send)
2. Partial deliverable identification
3. Calendar restructuring recommendations
4. Priority reshuffling
"""

from app.agents.base_agent import BaseAgent
from app.agents.registry import register_agent
from app.ai.parsers.intervention_parser import RecoveryPlanResponse
from app.ai.prompts.recovery_prompts import build_recovery_plan_prompt
from app.ai.prompts.system_prompts import get_recovery_system_prompt
from app.models.agent import AgentContext, AgentResult


@register_agent
class RecoveryAgent(BaseAgent):
    """Creates recovery plans when task completion becomes impossible."""

    name = "recovery_agent"

    async def _execute(self, context: AgentContext) -> AgentResult:
        if not context.task_id or not context.task_title:
            return AgentResult.failure_result(
                agent_name=self.name,
                error="RecoveryAgent requires task_id and task_title",
            )

        gemini = self._get_gemini_client()

        progress = context.task_progress or 0.0
        deadline = context.task_deadline or "Unknown"
        stakeholder = context.extra.get("stakeholder_hint")

        # Get all active tasks for rescheduling context
        all_tasks = []
        try:
            from app.services.task_service import TaskService
            task_service = TaskService()
            active = task_service.list_active_tasks(context.user_id)
            all_tasks = [
                {
                    "title": t.title,
                    "deadline": t.deadline,
                    "priority": t.priority,
                }
                for t in active[:8]
            ]
        except Exception:
            pass

        prompt = build_recovery_plan_prompt(
            failed_task_title=context.task_title,
            deadline=deadline,
            progress_percentage=progress,
            stakeholder_hint=stakeholder,
            all_active_tasks=all_tasks,
            genome_context=context.genome_context,
        )

        try:
            plan: RecoveryPlanResponse = await gemini.generate_structured(
                prompt=prompt,
                response_model=RecoveryPlanResponse,
                system_instruction=get_recovery_system_prompt(),
                agent_role="recovery",
                temperature=0.4,
            )
        except Exception as exc:
            self._logger.warning(
                "AI recovery plan failed — using template",
                error=str(exc),
            )
            return AgentResult.success_result(
                agent_name=self.name,
                data={
                    "extension_email_subject": f"Extension Request: {context.task_title}",
                    "extension_email_body": (
                        f"I am writing to request a brief extension for "
                        f'"{context.task_title}". I have completed approximately '
                        f"{progress:.0f}% of the work and need additional time "
                        f"to deliver quality results. I can provide a partial "
                        f"submission by the current deadline if needed."
                    ),
                    "partial_deliverable": "Current progress can be submitted as-is",
                    "revised_deadline": "",
                    "deprioritize_tasks": [],
                    "next_two_hours": [
                        "Assess current progress",
                        "Draft extension request",
                        "Identify what can be delivered now",
                    ],
                },
            )

        self._logger.info(
            "Recovery plan generated",
            task_id=context.task_id,
            deprioritize_count=len(plan.deprioritize_tasks),
        )

        return AgentResult.success_result(
            agent_name=self.name,
            data={
                "extension_email_subject": plan.extension_email_subject,
                "extension_email_body": plan.extension_email_body,
                "partial_deliverable": plan.partial_deliverable,
                "revised_deadline": plan.revised_deadline,
                "deprioritize_tasks": plan.deprioritize_tasks,
                "next_two_hours": plan.next_two_hours,
            },
        )