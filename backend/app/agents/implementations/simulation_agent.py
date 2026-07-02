"""
SPARK — Simulation Agent
Runs workload simulations to detect task collisions and overload.

Triggered:
- On task creation (detects new conflicts)
- Daily by Cloud Scheduler
- When Task Bankruptcy is being assessed

Output:
- Task collision predictions
- Overload date detection
- Bankruptcy risk assessment
"""

from datetime import datetime, timezone

from app.agents.base_agent import BaseAgent
from app.agents.registry import register_agent
from app.models.agent import AgentContext, AgentResult


@register_agent
class SimulationAgent(BaseAgent):
    """
    Simulates future workload to detect collisions and overload.
    Uses mathematical analysis rather than AI for speed.
    """

    name = "simulation_agent"

    async def _execute(self, context: AgentContext) -> AgentResult:
        """
        Analyzes all active tasks to detect workload conflicts.
        """
        from app.services.task_service import TaskService
        from app.services.genome_service import GenomeService

        task_service = TaskService()
        genome_service = GenomeService()

        try:
            active_tasks = task_service.list_active_tasks(context.user_id)
        except Exception as exc:
            return AgentResult.failure_result(
                agent_name=self.name,
                error=f"Could not fetch active tasks: {exc}",
            )

        if not active_tasks:
            return AgentResult.success_result(
                agent_name=self.name,
                data={
                    "task_collisions": [],
                    "overload_dates": [],
                    "bankruptcy_risk": False,
                    "total_remaining_hours": 0,
                    "available_hours_7d": 0,
                    "workload_ratio": 0,
                },
            )

        # Get user's productive capacity
        hours_per_day, _ = genome_service.get_working_hours(context.user_id)
        genome = genome_service.get_genome(context.user_id)
        underest_factor = genome.estimation.averageUnderestimationFactor

        now = datetime.now(timezone.utc)

        # Calculate total remaining work
        total_remaining_hours = 0
        task_deadlines: list[dict] = []

        for task in active_tasks:
            progress_fraction = task.progress.percentage / 100
            remaining = task.estimatedHours * (1 - progress_fraction) * underest_factor
            total_remaining_hours += remaining

            try:
                deadline = datetime.fromisoformat(
                    task.deadline.replace("Z", "+00:00")
                )
                hours_until = max((deadline - now).total_seconds() / 3600, 0)
            except (ValueError, AttributeError):
                hours_until = 168  # default 7 days

            task_deadlines.append({
                "task_id": task.id,
                "title": task.title,
                "remaining_hours": round(remaining, 1),
                "hours_until_deadline": round(hours_until, 1),
                "deadline": task.deadline,
                "priority": task.priority,
            })

        # Available hours in next 7 days
        available_hours_7d = hours_per_day * 7
        workload_ratio = total_remaining_hours / max(available_hours_7d, 0.1)

        # Detect collisions — tasks with overlapping deadline windows
        collisions = []
        sorted_tasks = sorted(task_deadlines, key=lambda t: t["hours_until_deadline"])

        cumulative_work = 0
        for i, task_info in enumerate(sorted_tasks):
            cumulative_work += task_info["remaining_hours"]
            available_by_deadline = task_info["hours_until_deadline"] * (hours_per_day / 24)

            if cumulative_work > available_by_deadline and i > 0:
                colliding_ids = [t["task_id"] for t in sorted_tasks[:i + 1]]
                collisions.append({
                    "task_ids": colliding_ids,
                    "collision_date": task_info["deadline"],
                    "severity": (
                        "critical" if cumulative_work > available_by_deadline * 1.5
                        else "medium"
                    ),
                    "cumulative_hours": round(cumulative_work, 1),
                    "available_hours": round(available_by_deadline, 1),
                })

        # Detect overload dates — days where work exceeds capacity
        overload_dates = []
        if workload_ratio > 1.2:
            overload_dates.append(now.isoformat())

        # Bankruptcy risk — is the total workload mathematically impossible?
        bankruptcy_risk = workload_ratio > 1.5

        self._logger.info(
            "Simulation complete",
            user_id=context.user_id,
            active_tasks=len(active_tasks),
            total_remaining=round(total_remaining_hours, 1),
            available_7d=round(available_hours_7d, 1),
            workload_ratio=round(workload_ratio, 2),
            collisions=len(collisions),
            bankruptcy_risk=bankruptcy_risk,
        )

        return AgentResult.success_result(
            agent_name=self.name,
            data={
                "task_deadlines": task_deadlines,
                "task_collisions": collisions,
                "overload_dates": overload_dates,
                "bankruptcy_risk": bankruptcy_risk,
                "total_remaining_hours": round(total_remaining_hours, 1),
                "available_hours_7d": round(available_hours_7d, 1),
                "workload_ratio": round(workload_ratio, 2),
            },
        )