"""
SPARK — Intervention Agent Prompts
Prompts for generating contextual interventions at each level.
"""


def build_intervention_prompt(
    task_title: str,
    intervention_level: int,
    failure_risk: float,
    cms_score: float,
    hours_until_deadline: float,
    hours_until_ponr: float | None,
    next_milestone: str | None,
    genome_context: str,
) -> str:
    """
    Builds the intervention prompt calibrated to the specific level.
    """
    level_descriptions = {
        0: "passive monitoring — no action needed",
        1: "gentle nudge — a single encouraging observation",
        2: "momentum assistance — break work into micro-steps",
        3: "active collaboration — guide through the next hour step by step",
        4: "critical intervention — urgent restructuring required",
        5: "recovery mode — minimize damage from likely failure",
    }

    ponr_context = (
        f"Point of No Return in {hours_until_ponr:.1f} hours — CRITICAL"
        if hours_until_ponr is not None and hours_until_ponr < 4
        else "PONR not yet critical"
    )

    next_ms = next_milestone or "No specific next milestone identified"

    return f"""Generate a Level {intervention_level} intervention for this task.

SITUATION:
Task: {task_title}
Failure risk: {failure_risk:.0%}
Momentum score: {cms_score:.0f}/100
Hours until deadline: {hours_until_deadline:.1f}h
PONR status: {ponr_context}
Next milestone: {next_ms}

INTERVENTION LEVEL {intervention_level}: {level_descriptions[intervention_level]}

USER CONTEXT:
{genome_context}

Generate:
1. The intervention message (conversational, appropriate urgency for level {intervention_level})
2. The specific next action required
3. Estimated time to complete that action (minutes)
4. Why this action was chosen (one sentence rationale)

Communication style must match level:
- Levels 1-2: Warm, encouraging, low pressure
- Levels 3-4: Direct, focused, action-oriented
- Level 5: Clear, honest, damage-minimizing
"""


def build_collaboration_prompt(
    task_title: str,
    current_step: str,
    user_message: str,
    conversation_history: list[dict],
    genome_context: str,
) -> str:
    """
    Builds the prompt for the Level 3 real-time collaboration chat.
    """
    history_str = "\n".join(
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in conversation_history[-6:]  # Last 6 turns for context
    )

    return f"""You are collaborating with the user in real-time to complete a task step.

TASK: {task_title}
CURRENT STEP: {current_step}

CONVERSATION HISTORY:
{history_str}

USER JUST SAID: {user_message}

USER CONTEXT:
{genome_context}

Respond as a focused work collaborator:
- Keep response under 100 words
- Guide them toward completing the current step
- If they're stuck, break it into an even smaller action
- If they completed it, celebrate briefly and move to the next step
- Stay on task — do not get distracted by off-topic conversation
"""