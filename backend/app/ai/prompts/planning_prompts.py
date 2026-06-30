"""
SPARK — Planning Agent Prompts
Prompts for task decomposition and milestone generation.
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
    Builds the prompt for the Planner Agent to decompose a task into milestones.

    Args:
        task_title: The task name
        task_description: Full task description
        deadline: ISO deadline string
        estimated_hours: User's estimate of total hours needed
        complexity: low | medium | high
        category: academic | work | personal
        genome_context: Compressed behavioral context from the Completion Genome
    """
    now = datetime.now(timezone.utc).isoformat()

    return f"""Create a detailed execution plan for the following task.

TASK INFORMATION:
Title: {task_title}
Description: {task_description}
Category: {category}
Complexity: {complexity}
Deadline: {deadline}
Estimated hours: {estimated_hours}
Current time: {now}

USER BEHAVIORAL CONTEXT:
{genome_context}

Generate a milestone-based execution plan. Each milestone should be:
- Completable in a single focused work session (25-90 minutes)
- Specific enough to start immediately without further planning
- Ordered so completion of each milestone enables the next
- The first milestone must be achievable in the next 30 minutes

Consider the user's behavioral patterns when estimating milestone durations.
If the user historically underestimates, add appropriate buffer time.
"""


def build_timeline_prompt(
    task_title: str,
    milestones: list[dict],
    available_hours_per_day: float,
    deadline: str,
) -> str:
    """
    Builds a prompt for generating a realistic timeline given available hours.
    """
    milestones_str = "\n".join(
        f"- {m['title']} ({m['estimated_minutes']} min)" for m in milestones
    )

    return f"""Given the following milestones for "{task_title}", create a realistic timeline.

MILESTONES:
{milestones_str}

CONSTRAINTS:
- Available working hours per day: {available_hours_per_day}
- Deadline: {deadline}
- Current time: {datetime.now(timezone.utc).isoformat()}

Determine if this task can be completed before the deadline.
If yes, assign specific dates to each milestone.
If no, identify which milestones could be cut or compressed.
"""