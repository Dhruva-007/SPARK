"""
SPARK — CMS Worker (Enhanced)
Full AI pipeline: CMS → Risk → Intervention Agent → Memory.
"""

from app.core.logging import get_logger

logger = get_logger(__name__)


async def run_cms_worker(user_id: str) -> dict:
    """
    Full CMS recalculation pipeline for all active tasks.

    For each task:
    1. Mathematical CMS calculation
    2. PONR recalculation
    3. If risk exceeds threshold → Intervention Agent generates message
    4. Intervention stored in Firestore
    5. Memory updated
    """
    from app.services.cms_service import CMSService
    from app.services.ponr_service import PONRService
    from app.services.intervention_service import InterventionService
    from app.services.task_service import TaskService
    from app.agents.orchestrator import AgentOrchestrator
    from app.memory.short_term import ShortTermMemory

    cms_service = CMSService()
    ponr_service = PONRService()
    intervention_service = InterventionService()
    task_service = TaskService()
    orchestrator = AgentOrchestrator()
    stm = ShortTermMemory()

    active_tasks = task_service.list_active_tasks(user_id)

    processed = 0
    interventions_created = 0
    errors = []

    for task in active_tasks:
        try:
            # Step 1: CMS recalculation
            cms_result = cms_service.recalculate_for_task(task.id, user_id)

            # Step 2: PONR recalculation
            ponr_result = ponr_service.recalculate_for_task(task.id, user_id)

            # Step 3: Check if intervention needed
            failure_risk = cms_result.failure_risk
            if intervention_service.should_intervene(task, failure_risk):
                level = intervention_service.determine_level(failure_risk)

                # Step 4: Run Intervention Agent for AI message
                try:
                    context = await orchestrator.build_context(
                        user_id=user_id, task_id=task.id
                    )
                    context.extra.update({
                        "intervention_level": level,
                        "failure_risk": failure_risk,
                        "cms_score": cms_result.score,
                        "hours_until_deadline": ponr_result.remaining_available_hours,
                        "hours_until_ponr": (
                            None if ponr_result.ponr_passed
                            else ponr_result.hours_until_ponr
                        ),
                    })

                    agent_result = await orchestrator.run_agent(
                        "intervention_agent", context
                    )

                    if agent_result.success and agent_result.data:
                        message = agent_result.data.get("message", "")
                        action = agent_result.data.get("next_action")
                    else:
                        message = _fallback_message(task.title, level, failure_risk)
                        action = None

                except Exception as exc:
                    logger.warning(
                        "Intervention agent failed — using fallback",
                        error=str(exc),
                    )
                    message = _fallback_message(task.title, level, failure_risk)
                    action = None

                # Step 5: Create intervention
                trigger = (
                    "ponr_approaching" if ponr_result.ponr_passed
                    else "risk_threshold"
                )
                intervention_service.create_intervention(
                    task=task,
                    user_id=user_id,
                    failure_risk=failure_risk,
                    message=message,
                    action_required=action,
                    trigger=trigger,
                )
                interventions_created += 1

                # Step 6: Record in memory
                try:
                    from app.memory.short_term import OBS_INTERVENTION_FIRED
                    stm.record(
                        user_id=user_id,
                        observation_type=OBS_INTERVENTION_FIRED,
                        data={"level": level, "risk": failure_risk},
                        task_id=task.id,
                    )
                except Exception:
                    pass

            # Step 5 (alternative): Run Recovery Agent if PONR passed
            if ponr_result.ponr_passed and failure_risk > 85:
                try:
                    context = await orchestrator.build_context(
                        user_id=user_id, task_id=task.id
                    )
                    await orchestrator.run_agent("recovery_agent", context)
                except Exception as exc:
                    logger.warning(
                        "Recovery agent failed",
                        task_id=task.id,
                        error=str(exc),
                    )

            processed += 1

        except Exception as exc:
            errors.append({"task_id": task.id, "error": str(exc)})
            logger.error(
                "CMS worker failed for task",
                task_id=task.id,
                error=str(exc),
            )

    logger.info(
        "CMS worker completed",
        user_id=user_id,
        processed=processed,
        interventions=interventions_created,
        errors=len(errors),
    )

    return {
        "processed": processed,
        "interventions_created": interventions_created,
        "errors": errors,
    }


def _fallback_message(task_title: str, level: int, risk: float) -> str:
    """Generates a fallback message when AI is unavailable."""
    messages = {
        1: f'"{task_title}" could use some attention. Risk: {risk:.0f}%',
        2: f'"{task_title}" needs momentum. Try a 25-minute focused sprint.',
        3: f'"{task_title}" is at {risk:.0f}% risk. Let\'s work on it together.',
        4: f'URGENT: "{task_title}" is at {risk:.0f}% failure risk.',
        5: f'CRITICAL: "{task_title}" — entering recovery mode.',
    }
    return messages.get(level, messages[2])