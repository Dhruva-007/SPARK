"""
SPARK — Reflection Agent Prompts
Prompts for post-task analysis and Completion Genome updates.
"""


def build_reflection_prompt(
    task_title: str,
    completion_status: str,
    deadline: str,
    completed_at: str | None,
    estimated_hours: float,
    actual_hours: float,
    interventions_used: list[dict],
    milestones_completed: int,
    milestones_total: int,
    current_genome: dict,
) -> str:
    """
    Builds the reflection prompt for post-task behavioral analysis.
    """
    days_late = ""
    if completion_status == "late" and completed_at:
        days_late = f"Completed {completed_at} (after deadline {deadline})"

    estimation_ratio = actual_hours / max(estimated_hours, 0.1)

    interventions_str = "\n".join(
        f"- Level {iv['level']} at {iv['trigger']}: outcome={iv.get('outcome', 'unknown')}"
        for iv in interventions_used[:10]
    ) or "No interventions used"

    genome_str = (
        f"- Peak hours: {current_genome.get('productivity', {}).get('peakHours', [])}\n"
        f"- Avg focus duration: {current_genome.get('productivity', {}).get('averageFocusDuration', 0)} min\n"
        f"- Underestimation factor: {current_genome.get('estimation', {}).get('averageUnderestimationFactor', 1.0):.2f}\n"
        f"- Success rate: {current_genome.get('completion', {}).get('successRate', 0):.0%}\n"
        f"- Recovery pattern: {current_genome.get('procrastination', {}).get('recoveryPattern', 'unknown')}"
    )

    return f"""Analyze this completed task and generate Completion Genome updates.

TASK OUTCOME:
Title: {task_title}
Status: {completion_status}
{days_late}
Estimated hours: {estimated_hours:.1f}h
Actual hours: {actual_hours:.1f}h
Estimation ratio: {estimation_ratio:.2f} (1.0 = perfect, >1.0 = underestimated)
Milestones: {milestones_completed}/{milestones_total} completed

INTERVENTIONS USED:
{interventions_str}

CURRENT GENOME (for context):
{genome_str}

Generate:
1. What worked well (2-3 specific observations)
2. What caused delays (2-3 specific observations)
3. Which interventions were effective and why
4. Specific genome parameter updates with exact values:
   - New underestimation factor for this task category
   - Peak productivity hours observed
   - Recovery pattern reinforcement/change
   - Intervention effectiveness scores
5. A 2-sentence behavioral summary for the user
"""