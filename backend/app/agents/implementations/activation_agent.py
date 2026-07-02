"""
SPARK — Activation Agent
Eliminates the blank page problem by generating starter materials.

Triggered: asynchronously after task creation
Input: task details + execution plan + genome context
Output: document outline, checklist, first action

The Activation Agent runs after PlannerAgent has generated milestones.
It creates:
1. A structured Google Doc outline (Phase 8+: real Docs API)
2. A concrete first-action checklist
3. The single smallest possible first step

In Phase 8, the Google Doc creation is simulated.
Phase 10 connects the real Google Docs API.
"""

from app.agents.base_agent import BaseAgent
from app.agents.registry import register_agent
from app.ai.prompts.activation_prompts import (
    build_activation_prompt,
    build_document_outline_prompt,
)
from app.ai.prompts.system_prompts import get_activation_system_prompt
from app.models.agent import AgentContext, AgentResult


class ActivationOutput:
    """Structured output from the Activation Agent."""
    pass


@register_agent
class ActivationAgent(BaseAgent):
    """
    Generates starter materials to eliminate blank-page paralysis.
    """

    name = "activation_agent"

    async def _execute(self, context: AgentContext) -> AgentResult:
        """
        Generates activation package: outline + checklist + first step.
        """
        if not context.task_id or not context.task_title:
            return AgentResult.failure_result(
                agent_name=self.name,
                error="ActivationAgent requires task_id and task_title",
            )

        gemini = self._get_gemini_client()

        # Get milestones from context extra data
        milestones = context.extra.get("milestones", [])

        # Build activation prompt
        prompt = build_activation_prompt(
            task_title=context.task_title,
            task_description=context.task_description or "",
            category=context.task_category or "personal",
            complexity=context.task_complexity or "medium",
            milestones=milestones,
            genome_context=context.genome_context,
        )

        try:
            # Generate activation content as text (structured format)
            activation_text = await gemini.generate(
                prompt=prompt,
                system_instruction=get_activation_system_prompt(),
                agent_role="activation",
                temperature=0.5,
            )
        except Exception as exc:
            return AgentResult.failure_result(
                agent_name=self.name,
                error=f"Gemini generation failed: {exc}",
            )

        # Generate document outline separately
        try:
            outline_text = await gemini.generate(
                prompt=build_document_outline_prompt(
                    task_title=context.task_title,
                    task_description=context.task_description or "",
                    category=context.task_category or "personal",
                ),
                system_instruction=get_activation_system_prompt(),
                agent_role="activation",
                temperature=0.3,
            )
        except Exception as exc:
            self._logger.warning("Outline generation failed", error=str(exc))
            outline_text = f"# {context.task_title}\n\n## Overview\n\n## Steps\n\n## Notes"

        self._logger.info(
            "Activation package generated",
            task_id=context.task_id,
            has_outline=bool(outline_text),
            has_activation=bool(activation_text),
        )

        # Phase 10+: Create actual Google Doc here
        # For now, store the outline content
        activation_data = {
            "activation_content": activation_text,
            "document_outline": outline_text,
            "google_doc_id": None,        # Phase 10: real Doc ID
            "google_doc_url": None,       # Phase 10: real Doc URL
            "checklist_generated": True,
            "outline_generated": True,
        }

        # Update task activation in Firestore
        try:
            from app.repositories.task_repository import TaskRepository
            task_repo = TaskRepository()
            task_repo.update_activation(
                task_id=context.task_id,
                google_doc_id=None,
                google_doc_url=None,
                checklist_generated=True,
                outline_generated=True,
            )
        except Exception as exc:
            self._logger.warning(
                "Could not update task activation status",
                error=str(exc),
            )

        return AgentResult.success_result(
            agent_name=self.name,
            data=activation_data,
        )