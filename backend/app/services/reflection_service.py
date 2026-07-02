"""
SPARK — Reflection Service (Enhanced)
Triggers the ReflectionAgent after task completion.
"""

from datetime import datetime, timezone

from app.core.logging import get_logger
from app.models.task import Task
from app.models.intervention import Reflection
from app.repositories.intervention_repository import InterventionRepository
from app.services.genome_service import GenomeService

logger = get_logger(__name__)


class ReflectionService:
    """Manages post-completion reflection with AI analysis."""

    def __init__(self) -> None:
        self._intervention_repo = InterventionRepository()
        self._genome_service = GenomeService()

    async def create_reflection(
        self,
        task: Task,
        user_id: str,
    ) -> Reflection:
        """
        Creates a reflection record and runs the ReflectionAgent.
        """
        now = datetime.now(timezone.utc)

        # Determine completion status
        try:
            deadline = datetime.fromisoformat(
                task.deadline.replace("Z", "+00:00")
            )
            completed_at = datetime.fromisoformat(
                task.completedAt.replace("Z", "+00:00")
            ) if task.completedAt else now

            if completed_at <= deadline:
                completion_status = "on_time"
                deadline_met = True
                days_late = None
            else:
                completion_status = "late"
                deadline_met = False
                days_late = (completed_at - deadline).total_seconds() / 86400
        except (ValueError, AttributeError):
            completion_status = "on_time"
            deadline_met = True
            days_late = None
            completed_at = now

        # Get interventions used for this task
        interventions = self._intervention_repo.list_by_task(task.id)
        interventions_used = [
            {
                "level": i.level,
                "trigger": i.trigger,
                "outcome": i.outcome,
            }
            for i in interventions
        ]

        # Estimation accuracy
        estimated = task.estimatedHours
        actual = task.actualHoursSpent if task.actualHoursSpent > 0 else estimated

        # Run ReflectionAgent for AI analysis
        ai_analysis = {}
        try:
            from app.agents.orchestrator import AgentOrchestrator

            orchestrator = AgentOrchestrator()
            context = await orchestrator.build_context(
                user_id=user_id, task_id=task.id
            )
            context.extra.update({
                "completion_status": completion_status,
                "completed_at": completed_at.isoformat(),
                "actual_hours": actual,
                "interventions_used": interventions_used,
                "milestones_completed": task.progress.milestonesCurrent,
                "milestones_total": task.progress.milestonesTotal,
            })

            result = await orchestrator.run_agent("reflection_agent", context)
            if result.success and result.data:
                ai_analysis = result.data

        except Exception as exc:
            logger.warning(
                "ReflectionAgent failed — creating basic reflection",
                error=str(exc),
            )

        # Build reflection record
        reflection = Reflection(
            userId=user_id,
            taskId=task.id,
            taskTitle=task.title,
            completionStatus=completion_status,
            deadlineMet=deadline_met,
            daysLate=round(days_late, 1) if days_late else None,
            analysis={
                "estimationAccuracy": round(estimated / max(actual, 0.1), 2),
                "progressAtCompletion": task.progress.percentage,
                "totalInterventions": len(interventions),
                "whatWorked": ai_analysis.get("what_worked", []),
                "whatCausedDelays": ai_analysis.get("what_caused_delays", []),
                "effectiveInterventions": ai_analysis.get(
                    "effective_interventions", []
                ),
            },
            genomeUpdates=[],
            summary=ai_analysis.get(
                "behavioral_summary",
                f"Task '{task.title}' completed {completion_status}.",
            ),
            insights=ai_analysis.get("what_worked", [])
            + ai_analysis.get("what_caused_delays", []),
        )

        created = self._intervention_repo.create_reflection(reflection)

        # Update genome statistics
        self._genome_service.record_task_completion(
            user_id=user_id,
            succeeded=task.status == "completed",
            deadline_met=deadline_met,
        )

        logger.info(
            "Reflection created",
            task_id=task.id,
            status=completion_status,
            has_ai_analysis=bool(ai_analysis),
        )

        return created

    def list_reflections(
        self, user_id: str, limit: int = 20
    ) -> list[Reflection]:
        return self._intervention_repo.list_reflections(user_id, limit=limit)