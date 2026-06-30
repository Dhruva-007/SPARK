"""
SPARK — Recovery Agent Prompts
Prompts for damage minimization when tasks cannot be completed.
"""

from datetime import datetime, timezone


def build_recovery_plan_prompt(
    failed_task_title: str,
    deadline: str,
    progress_percentage: float,
    stakeholder_hint: str | None,
    all_active_tasks: list[dict],
    genome_context: str,
) -> str:
    """
    Builds the recovery plan prompt when a task cannot be completed on time.
    """
    now = datetime.now(timezone.utc).isoformat()
    tasks_str = "\n".join(
        f"- {t['title']} (deadline: {t['deadline']}, priority: {t['priority']})"
        for t in all_active_tasks[:8]
    )
    stakeholder = stakeholder_hint or "the relevant stakeholder"

    return f"""Create a recovery plan for a task that cannot be completed before its deadline.

FAILED TASK:
Title: {failed_task_title}
Deadline: {deadline}
Current progress: {progress_percentage:.0f}%
Current time: {now}

OTHER ACTIVE TASKS (for rescheduling context):
{tasks_str}

STAKEHOLDER: {stakeholder}

USER BEHAVIORAL CONTEXT:
{genome_context}

Generate a complete recovery plan:
1. Extension request email (professional, honest, solution-focused)
2. What partial work can be delivered by the deadline
3. Revised completion timeline
4. Which other tasks should be deprioritized to focus on recovery
5. Specific actions for the next 2 hours to minimize damage

The email should be written in first person, ready to send with minimal editing.
"""


def build_bankruptcy_assessment_prompt(
    all_tasks: list[dict],
    available_hours_next_7_days: float,
    genome_context: str,
) -> str:
    """
    Builds the prompt for assessing whether task bankruptcy is needed.
    """
    now = datetime.now(timezone.utc).isoformat()
    tasks_str = "\n".join(
        f"- {t['title']} | deadline: {t['deadline']} | "
        f"progress: {t.get('progress', 0):.0f}% | "
        f"priority: {t['priority']} | "
        f"estimated remaining: {t.get('remaining_hours', 0):.1f}h"
        for t in all_tasks
    )

    return f"""Assess whether this user's workload requires Task Bankruptcy intervention.

Task Bankruptcy is declared when it is mathematically impossible to complete
all tasks on time, and strategic sacrifice is required.

CURRENT WORKLOAD:
{tasks_str}

CAPACITY:
Available productive hours in next 7 days: {available_hours_next_7_days:.1f}h
Current time: {now}

USER BEHAVIORAL CONTEXT:
{genome_context}

Provide:
1. Is bankruptcy needed? (true/false)
2. If yes: which tasks to prioritize (keep)
3. If yes: which tasks to sacrifice (defer/drop)
4. Prioritization rationale (impact, deadline proximity, recovery options)
5. The single most important task to focus on immediately
6. Overall workload reduction recommendation
"""