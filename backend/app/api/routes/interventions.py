"""
SPARK — Intervention Routes
Complete intervention management with AI chat and recovery plans.
"""

from typing import Any

from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from app.api.dependencies import CurrentUser
from app.core.logging import get_logger
from app.models.common import success_response
from app.services.intervention_service import InterventionService

router = APIRouter()
logger = get_logger(__name__)

_intervention_service = InterventionService()


@router.get("/interventions", summary="List all active interventions")
async def list_interventions(user: CurrentUser) -> dict[str, Any]:
    """Lists all active (unresolved) interventions across all tasks."""
    from app.services.task_service import TaskService
    task_service = TaskService()
    active_tasks = task_service.list_active_tasks(user.uid)

    all_interventions = []
    for task in active_tasks:
        try:
            task_interventions = _intervention_service.list_active_interventions(
                task.id
            )
            for iv in task_interventions:
                data = iv.model_dump()
                data["taskTitle"] = task.title
                all_interventions.append(data)
        except Exception:
            pass

    return success_response(
        data={
            "interventions": all_interventions,
            "total": len(all_interventions),
        }
    )


@router.get(
    "/tasks/{task_id}/interventions",
    summary="List task interventions",
)
async def list_task_interventions(
    task_id: str,
    user: CurrentUser,
) -> dict[str, Any]:
    interventions = _intervention_service.list_task_interventions(task_id)
    return success_response(
        data={
            "interventions": [i.model_dump() for i in interventions],
            "task_id": task_id,
        }
    )


@router.post(
    "/interventions/{intervention_id}/respond",
    summary="Respond to an intervention",
)
async def respond_to_intervention(
    intervention_id: str,
    user: CurrentUser,
    body: dict = Body(...),
) -> dict[str, Any]:
    """Accepts or dismisses an intervention."""
    task_id = body.get("task_id", "")
    outcome = body.get("outcome", "dismissed")

    _intervention_service.resolve_intervention(
        task_id=task_id,
        intervention_id=intervention_id,
        outcome=outcome,
    )

    # Record in memory
    try:
        from app.memory.short_term import ShortTermMemory, OBS_INTERVENTION_OUTCOME
        stm = ShortTermMemory()
        stm.record(
            user_id=user.uid,
            observation_type=OBS_INTERVENTION_OUTCOME,
            data={"intervention_id": intervention_id, "outcome": outcome},
            task_id=task_id if task_id else None,
        )

        from app.memory.long_term import LongTermMemory
        ltm = LongTermMemory()
        was_effective = outcome in ("accepted", "completed")
        interventions = _intervention_service.list_task_interventions(task_id)
        matched = next(
            (i for i in interventions if i.id == intervention_id),
            None,
        )
        if matched:
            ltm.update_intervention_effectiveness(
                user_id=user.uid,
                level=matched.level,
                was_effective=was_effective,
            )
    except Exception as exc:
        logger.warning("Memory update failed", error=str(exc))

    return success_response(
        data={"intervention_id": intervention_id, "outcome": outcome}
    )


@router.post("/interventions/chat", summary="Chat with Intervention Agent")
async def intervention_chat(
    user: CurrentUser,
    body: dict = Body(...),
) -> dict[str, Any]:
    """
    Sends a message to the Intervention Agent and returns a response.
    Used for Level 3 active collaboration.
    """
    task_id = body.get("task_id")
    message = body.get("message", "")
    conversation_history = body.get("history", [])

    if not task_id or not message:
        return success_response(
            data={"error": "task_id and message are required"}
        )

    from app.agents.orchestrator import AgentOrchestrator
    from app.ai.gemini_client import get_gemini_client
    from app.ai.prompts.intervention_prompts import build_collaboration_prompt

    orchestrator = AgentOrchestrator()
    context = await orchestrator.build_context(
        user_id=user.uid, task_id=task_id
    )

    current_step = context.extra.get(
        "next_milestone", "Current task milestone"
    )

    prompt = build_collaboration_prompt(
        task_title=context.task_title or "Task",
        current_step=current_step,
        user_message=message,
        conversation_history=conversation_history,
        genome_context=context.genome_context,
    )

    try:
        client = get_gemini_client()
        from app.ai.prompts.system_prompts import get_intervention_system_prompt
        response = await client.generate(
            prompt=prompt,
            system_instruction=get_intervention_system_prompt(),
            agent_role="intervention",
            temperature=0.7,
        )

        return success_response(
            data={
                "response": response,
                "task_id": task_id,
            }
        )
    except Exception as exc:
        logger.error("Intervention chat failed", error=str(exc))
        return success_response(
            data={
                "response": "I'm having trouble connecting right now. Try breaking your current step into an even smaller action.",
                "error": str(exc),
            }
        )


@router.post(
    "/tasks/{task_id}/recovery-plan",
    summary="Generate a recovery plan",
)
async def generate_recovery_plan(
    task_id: str,
    user: CurrentUser,
) -> dict[str, Any]:
    """Runs the Recovery Agent for a task that has passed PONR."""
    from app.agents.orchestrator import AgentOrchestrator

    orchestrator = AgentOrchestrator()
    context = await orchestrator.build_context(
        user_id=user.uid, task_id=task_id
    )

    result = await orchestrator.run_agent("recovery_agent", context)

    if result.success:
        return success_response(data=result.data)
    else:
        return success_response(
            data={"error": result.error}
        )