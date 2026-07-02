"""
SPARK — Planning Agent Prompts
"""

from datetime import datetime, timezone


def build_task_planning_prompt(
    task_title: str,
    task_description: str,
    deadline: str,
    estimated_hours: float,
    complexity: str,
    category: str,
    genome_context: str,
) -> str:
    """
    Builds the prompt for the Planner Agent.
    Kept concise to preserve token budget for the response.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""Create an execution plan for this task.

TASK: {task_title}
DESCRIPTION: {task_description}
CATEGORY: {category}
COMPLEXITY: {complexity}
DEADLINE: {deadline}
ESTIMATED HOURS: {estimated_hours}
CURRENT TIME: {now}

USER BEHAVIORAL CONTEXT: {genome_context}

Generate 3 to 6 milestones. Each milestone must be completable in one focused session.
The first milestone must be achievable in 30 minutes or less.
Make milestones specific enough that the user can start immediately without further planning.

Also provide:
- first_action: the single smallest possible action (under 5 minutes, starts immediately)
- total_estimated_hours: realistic total hours accounting for user behavioral patterns
- implicit_requirements: any hidden requirements not stated explicitly
- confidence: your confidence in this plan (0.0 to 1.0)"""


def build_timeline_prompt(
    task_title: str,
    milestones: list[dict],
    available_hours_per_day: float,
    deadline: str,
) -> str:
    milestones_str = "\n".join(
        f"- {m['title']} ({m['estimated_minutes']} min)"
        for m in milestones
    )

    return f"""Given milestones for "{task_title}", create a realistic timeline.

MILESTONES:
{milestones_str}

Available hours per day: {available_hours_per_day}
Deadline: {deadline}

Determine if this is achievable before the deadline.
If yes, assign dates to each milestone.
If no, identify what can be cut or compressed."""