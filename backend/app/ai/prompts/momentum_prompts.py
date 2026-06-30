"""
SPARK — Momentum Agent Prompts
Prompts for calculating CMS and identifying next best actions.
"""

from datetime import datetime, timezone


def build_next_action_prompt(
    task_title: str,
    current_progress: float,
    last_milestone_completed: str | None,
    next_milestone: str | None,
    hours_until_deadline: float,
    cms_score: float,
    genome_context: str,
) -> str:
    """
    Builds the prompt for identifying the single next best action.
    """
    last_action = last_milestone_completed or "Nothing yet — task just started"
    next_ms = next_milestone or "No milestones defined yet"
    now = datetime.now(timezone.utc).isoformat()

    return f"""Identify the single next action that will best maintain momentum on this task.

TASK STATUS:
Task: {task_title}
Current progress: {current_progress:.0f}%
Momentum score: {cms_score:.0f}/100
Hours until deadline: {hours_until_deadline:.1f}h
Current time: {now}

MILESTONE CONTEXT:
Last completed: {last_action}
Next milestone: {next_ms}

USER BEHAVIORAL CONTEXT:
{genome_context}

Identify ONE specific action. Rules:
- Completable in the next 25-45 minutes
- Specific enough to start without further thought
- Build on what has already been done
- If momentum is below 40, suggest the smallest possible action
- If momentum is above 70, suggest something more substantial

Output the action as a single clear sentence starting with a verb.
"""


def build_cms_calculation_prompt(
    task_title: str,
    progress_percentage: float,
    hours_elapsed: float,
    hours_until_deadline: float,
    estimated_total_hours: float,
    milestones_completed: int,
    milestones_total: int,
    genome_context: str,
) -> str:
    """
    Builds the prompt for calculating a nuanced Completion Momentum Score.
    The mathematical base is calculated in CMSService — this provides
    the qualitative adjustment based on behavioral patterns.
    """
    velocity = progress_percentage / max(hours_elapsed, 0.1)
    hours_remaining_work = estimated_total_hours * (1 - progress_percentage / 100)

    return f"""Calculate a Completion Momentum Score adjustment for this task.

MATHEMATICAL BASELINE:
Task: {task_title}
Progress: {progress_percentage:.1f}%
Work velocity: {velocity:.2f}% per hour
Hours elapsed: {hours_elapsed:.1f}h
Hours until deadline: {hours_until_deadline:.1f}h
Estimated remaining work: {hours_remaining_work:.1f}h
Milestones: {milestones_completed}/{milestones_total} complete

USER BEHAVIORAL CONTEXT:
{genome_context}

Given the user's historical patterns, provide:
1. A score adjustment (-20 to +20) to apply to the mathematical baseline
2. The primary factor driving this adjustment
3. The failure risk percentage (0-100)
4. A trend direction: improving | stable | declining | critical

Base the adjustment on whether this user typically accelerates or slows
as deadlines approach, and their historical accuracy for this task type.
"""