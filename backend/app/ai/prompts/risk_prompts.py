"""
SPARK — Risk Prediction Agent Prompts
Prompts for calculating failure probability and PONR.
"""

from datetime import datetime, timezone


def build_risk_assessment_prompt(
    task_title: str,
    progress_percentage: float,
    hours_until_deadline: float,
    estimated_remaining_hours: float,
    available_productive_hours: float,
    active_task_count: int,
    genome_context: str,
) -> str:
    """
    Builds the prompt for calculating comprehensive failure risk.
    """
    now = datetime.now(timezone.utc).isoformat()
    feasibility_ratio = (
        available_productive_hours / max(estimated_remaining_hours, 0.1)
    )

    return f"""Assess the failure risk for this task with precision.

TASK METRICS:
Task: {task_title}
Progress: {progress_percentage:.1f}%
Hours until deadline: {hours_until_deadline:.1f}h
Estimated remaining work: {estimated_remaining_hours:.1f}h
Available productive hours before deadline: {available_productive_hours:.1f}h
Feasibility ratio: {feasibility_ratio:.2f} (>1.0 = achievable, <1.0 = at risk)
Competing active tasks: {active_task_count}
Current time: {now}

USER BEHAVIORAL PATTERNS:
{genome_context}

Provide:
1. Failure probability (0.0 to 1.0) — be precise, not rounded
2. Primary risk factor (single sentence)
3. Point of No Return timestamp — when must work begin to still succeed?
4. Recommended intervention level (0-5)
5. One specific action that would most reduce the risk right now

Consider how this user's behavioral patterns affect the mathematical feasibility.
A user who consistently sprints near deadlines may succeed despite low current progress.
"""


def build_ponr_calculation_prompt(
    task_title: str,
    remaining_work_hours: float,
    deadline: str,
    available_hours_per_day: float,
    user_productivity_pattern: str,
) -> str:
    """
    Builds the prompt for calculating the Point of No Return.
    """
    return f"""Calculate the precise Point of No Return for this task.

The Point of No Return (PONR) is the latest moment at which work must begin
for the task to be completable before the deadline.

TASK: {task_title}
Remaining work: {remaining_work_hours:.1f} hours
Deadline: {deadline}
Available hours per day: {available_hours_per_day:.1f}h
User productivity pattern: {user_productivity_pattern}

Calculate:
1. The PONR timestamp (ISO format)
2. Hours remaining until PONR
3. Whether PONR has already passed
4. Confidence level in this calculation (low/medium/high)

Factor in that users rarely work at 100% efficiency.
Apply a realistic productivity factor based on the user's pattern.
"""