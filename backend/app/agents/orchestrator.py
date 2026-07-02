"""
SPARK — Agent Orchestrator
Coordinates multi-agent workflows.
MemoryAgent now runs first to enrich context before other agents.
"""

from datetime import datetime, timezone
from typing import Optional

from app.core.logging import get_logger
from app.models.agent import AgentContext, AgentResult

logger = get_logger(__name__)


class AgentOrchestrator:
    """Coordinates SPARK agent execution and multi-agent workflows."""

    def __init__(self) -> None:
        self._logger = get_logger("agent_orchestrator")

    async def run_agent(
        self,
        agent_name: str,
        context: AgentContext,
    ) -> AgentResult:
        """
        Runs a single named agent with the provided context.
        Always returns AgentResult — never raises.
        """
        from app.agents.registry import get_agent, is_registered

        if not is_registered(agent_name):
            return AgentResult.failure_result(
                agent_name=agent_name,
                error=f"Agent '{agent_name}' is not registered",
            )

        agent = get_agent(agent_name)
        return await agent.run(context)

    async def build_context(
        self,
        user_id: str,
        task_id: Optional[str] = None,
    ) -> AgentContext:
        """
        Builds an AgentContext by gathering data from multiple sources.
        Now includes memory enrichment from MemoryAgent.
        """
        from app.services.genome_service import GenomeService
        from app.services.task_service import TaskService
        from app.repositories.user_repository import UserRepository

        genome_service = GenomeService()
        task_service = TaskService()
        user_repo = UserRepository()

        now_iso = datetime.now(timezone.utc).isoformat()

        # Get genome context (base — will be enriched by MemoryAgent)
        try:
            genome_context = genome_service.get_compressed_context(user_id)
        except Exception as exc:
            logger.warning("Could not get genome context", error=str(exc))
            genome_context = "No genome data available"

        # Get active task count
        try:
            active_tasks = task_service.list_active_tasks(user_id)
            active_task_count = len(active_tasks)
            active_task_titles = [t.title for t in active_tasks[:5]]
        except Exception as exc:
            logger.warning("Could not get active tasks", error=str(exc))
            active_task_count = 0
            active_task_titles = []

        # Get user settings
        try:
            user = user_repo.get_by_id(user_id)
            timezone_str = user.settings.timezone if user else "UTC"
            hours_start = user.settings.workingHoursStart if user else "09:00"
            hours_end = user.settings.workingHoursEnd if user else "17:00"
        except Exception as exc:
            logger.warning("Could not get user settings", error=str(exc))
            timezone_str = "UTC"
            hours_start = "09:00"
            hours_end = "17:00"

        context = AgentContext(
            user_id=user_id,
            task_id=task_id,
            genome_context=genome_context,
            active_task_count=active_task_count,
            active_task_titles=active_task_titles,
            current_time_iso=now_iso,
            user_timezone=timezone_str,
            working_hours_start=hours_start,
            working_hours_end=hours_end,
        )

        # Populate task-specific fields
        if task_id:
            try:
                task = task_service.get_task(task_id, user_id)
                context.task_title = task.title
                context.task_description = task.description
                context.task_deadline = task.deadline
                context.task_estimated_hours = task.estimatedHours
                context.task_complexity = task.complexity
                context.task_category = task.category
                context.task_progress = task.progress.percentage
                context.task_status = task.status
            except Exception as exc:
                logger.warning(
                    "Could not populate task context",
                    task_id=task_id,
                    error=str(exc),
                )

        # Enrich context with MemoryAgent
        context = await self._enrich_with_memory(context)

        return context

    async def _enrich_with_memory(self, context: AgentContext) -> AgentContext:
        """
        Runs MemoryAgent and merges the enriched genome context
        back into the AgentContext.
        This replaces the basic genome context with the full
        memory-enriched version.
        """
        try:
            memory_result = await self.run_agent("memory_agent", context)

            if memory_result.success and memory_result.data:
                data = memory_result.data
                # Replace basic genome context with memory-enriched version
                context.genome_context = data.get(
                    "enriched_genome_context",
                    context.genome_context,
                )
                # Store behavioral summary in extra for agents that need it
                context.extra["behavioral_summary"] = data.get(
                    "behavioral_summary", {}
                )
                context.extra["session_summary"] = data.get(
                    "session_summary", {}
                )
                context.extra["is_peak_hour"] = data.get("is_peak_hour", False)
                context.extra["preferred_intervention_level"] = data.get(
                    "preferred_intervention_level", 2
                )

                self._logger.debug(
                    "Context enriched with memory",
                    user_id=context.user_id,
                    is_peak_hour=context.extra.get("is_peak_hour"),
                )

        except Exception as exc:
            self._logger.warning(
                "Memory enrichment failed — using base context",
                error=str(exc),
            )

        return context

    async def run_task_creation_flow(
        self,
        user_id: str,
        task_id: str,
    ) -> dict:
        """
        Multi-agent workflow triggered when a task is created.
        Memory enrichment now happens automatically in build_context.
        """
        self._logger.info(
            "Starting task creation flow",
            user_id=user_id,
            task_id=task_id,
        )

        # Record task focus observation
        try:
            from app.memory.short_term import ShortTermMemory, OBS_TASK_FOCUSED
            stm = ShortTermMemory()
            stm.record(
                user_id=user_id,
                observation_type=OBS_TASK_FOCUSED,
                data={"action": "task_created"},
                task_id=task_id,
            )
        except Exception:
            pass

        # Build memory-enriched context
        context = await self.build_context(user_id=user_id, task_id=task_id)

        results: dict = {
            "task_id": task_id,
            "milestones_created": 0,
            "first_action": None,
            "errors": [],
        }

        # Run PlannerAgent
        planner_result = await self.run_agent("planner_agent", context)

        if planner_result.success and planner_result.data:
            plan_data = planner_result.data

            try:
                from app.repositories.milestone_repository import MilestoneRepository
                from app.models.milestone import Milestone

                milestone_repo = MilestoneRepository()
                milestones = []

                for ms_data in plan_data.get("milestones", []):
                    milestone = Milestone(
                        taskId=task_id,
                        title=ms_data["title"],
                        description=ms_data.get("description", ""),
                        order=ms_data["order"],
                        estimatedMinutes=ms_data["estimated_minutes"],
                        isNextAction=ms_data.get("is_first_action", False),
                    )
                    milestones.append(milestone)

                if milestones:
                    milestones[0].isNextAction = True
                    milestone_repo.batch_create(milestones)

                    from app.repositories.task_repository import TaskRepository
                    task_repo = TaskRepository()
                    task_repo.update(
                        task_id,
                        user_id,
                        {
                            "progress.milestonesTotal": len(milestones),
                            "progress.milestonesCurrent": 0,
                        },
                    )

                results["milestones_created"] = len(milestones)
                results["first_action"] = plan_data.get("first_action")

                self._logger.info(
                    "Milestones created from planning",
                    task_id=task_id,
                    count=len(milestones),
                )

            except Exception as exc:
                error_msg = f"Milestone storage failed: {exc}"
                results["errors"].append(error_msg)
                self._logger.error(
                    "Milestone storage failed",
                    task_id=task_id,
                    error=str(exc),
                )
        else:
            error_msg = planner_result.error or "PlannerAgent returned no data"
            results["errors"].append(f"PlannerAgent: {error_msg}")
            self._logger.warning(
                "PlannerAgent did not produce a plan",
                task_id=task_id,
                error=error_msg,
            )

        return results

    async def run_activation_flow(
        self,
        user_id: str,
        task_id: str,
    ) -> dict:
        """Runs the ActivationAgent for a task."""
        context = await self.build_context(user_id=user_id, task_id=task_id)
        activation_result = await self.run_agent("activation_agent", context)

        if activation_result.success:
            return activation_result.data or {}
        else:
            self._logger.warning(
                "Activation flow failed",
                task_id=task_id,
                error=activation_result.error,
            )
            return {"error": activation_result.error}

    async def run_momentum_check(
        self,
        user_id: str,
        task_id: str,
    ) -> dict:
        """Runs the MomentumAgent to get the next best action."""
        context = await self.build_context(user_id=user_id, task_id=task_id)

        # Record next action view
        try:
            from app.memory.short_term import ShortTermMemory, OBS_NEXT_ACTION_VIEWED
            stm = ShortTermMemory()
            stm.record(
                user_id=user_id,
                observation_type=OBS_NEXT_ACTION_VIEWED,
                data={"task_id": task_id},
                task_id=task_id,
            )
        except Exception:
            pass

        result = await self.run_agent("momentum_agent", context)
        return result.data if result.success else {}