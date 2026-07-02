"""
SPARK — Task Bankruptcy Service
Detects impossible workloads and orchestrates strategic task sacrifice.

Task Bankruptcy is declared when:
- Total remaining work exceeds available time by > 50%
- Multiple critical deadlines overlap with insufficient capacity
- The SimulationAgent detects bankruptcy_risk = true

When declared:
1. AI analyzes all tasks for impact and priority
2. Tasks are triaged: keep (prioritize) vs sacrifice (defer/drop)
3. Extension emails are drafted for sacrificed tasks
4. Calendar is restructured around priorities
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.core.logging import get_logger
from app.services.task_service import TaskService
from app.services.genome_service import GenomeService
from app.repositories.task_repository import TaskRepository

logger = get_logger(__name__)


class BankruptcyService:
    """Manages the Task Bankruptcy Engine."""

    def __init__(self) -> None:
        self._task_service = TaskService()
        self._genome_service = GenomeService()
        self._task_repo = TaskRepository()

    async def assess_bankruptcy(self, user_id: str) -> dict:
        """
        Runs the SimulationAgent and assesses whether bankruptcy is needed.
        Returns assessment data without declaring bankruptcy.
        """
        from app.agents.orchestrator import AgentOrchestrator

        orchestrator = AgentOrchestrator()
        context = await orchestrator.build_context(user_id=user_id)
        sim_result = await orchestrator.run_agent("simulation_agent", context)

        if not sim_result.success:
            return {
                "bankruptcy_needed": False,
                "error": sim_result.error,
                "message": "Could not assess workload — simulation failed",
            }

        sim_data = sim_result.data or {}
        bankruptcy_needed = sim_data.get("bankruptcy_risk", False)
        workload_ratio = sim_data.get("workload_ratio", 0)

        assessment = {
            "bankruptcy_needed": bankruptcy_needed,
            "workload_ratio": workload_ratio,
            "total_remaining_hours": sim_data.get("total_remaining_hours", 0),
            "available_hours_7d": sim_data.get("available_hours_7d", 0),
            "task_collisions": sim_data.get("task_collisions", []),
            "task_deadlines": sim_data.get("task_deadlines", []),
            "message": (
                "Workload exceeds capacity — Task Bankruptcy recommended"
                if bankruptcy_needed
                else "Workload is manageable"
            ),
        }

        if bankruptcy_needed:
            # Use AI to determine which tasks to prioritize
            try:
                triage = await self._ai_triage(user_id, sim_data)
                assessment.update(triage)
            except Exception as exc:
                logger.warning(
                    "AI triage failed — using priority-based fallback",
                    error=str(exc),
                )
                assessment.update(
                    self._fallback_triage(sim_data.get("task_deadlines", []))
                )

        return assessment

    async def _ai_triage(self, user_id: str, sim_data: dict) -> dict:
        """Uses Gemini to intelligently triage tasks."""
        from app.ai.gemini_client import get_gemini_client
        from app.ai.parsers.intervention_parser import BankruptcyAssessmentResponse
        from app.ai.prompts.recovery_prompts import build_bankruptcy_assessment_prompt

        genome = self._genome_service.get_genome(user_id)
        genome_context = genome.to_compressed_context()

        all_tasks = sim_data.get("task_deadlines", [])
        available_hours = sim_data.get("available_hours_7d", 40)

        prompt = build_bankruptcy_assessment_prompt(
            all_tasks=all_tasks,
            available_hours_next_7_days=available_hours,
            genome_context=genome_context,
        )

        client = get_gemini_client()
        result: BankruptcyAssessmentResponse = await client.generate_structured(
            prompt=prompt,
            response_model=BankruptcyAssessmentResponse,
            agent_role="recovery",
            temperature=0.2,
        )

        return {
            "prioritize_tasks": result.prioritize_task_titles,
            "sacrifice_tasks": result.sacrifice_task_titles,
            "rationale": result.prioritization_rationale,
            "focus_task": result.focus_task,
            "workload_reduction": result.workload_reduction,
        }

    def _fallback_triage(self, task_deadlines: list[dict]) -> dict:
        """Priority-based fallback when AI triage fails."""
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_tasks = sorted(
            task_deadlines,
            key=lambda t: (
                priority_order.get(t.get("priority", "low"), 3),
                t.get("hours_until_deadline", 999),
            ),
        )

        # Keep top 60% by priority, sacrifice the rest
        keep_count = max(1, int(len(sorted_tasks) * 0.6))
        keep = sorted_tasks[:keep_count]
        sacrifice = sorted_tasks[keep_count:]

        return {
            "prioritize_tasks": [t["title"] for t in keep],
            "sacrifice_tasks": [t["title"] for t in sacrifice],
            "rationale": "Priority-based triage (AI unavailable)",
            "focus_task": keep[0]["title"] if keep else "",
            "workload_reduction": "Defer low-priority tasks to free up capacity",
        }

    async def declare_bankruptcy(self, user_id: str) -> dict:
        """
        Officially declares Task Bankruptcy.
        Marks sacrificed tasks as bankrupt and stores the declaration.
        """
        assessment = await self.assess_bankruptcy(user_id)

        if not assessment.get("bankruptcy_needed"):
            return {
                "declared": False,
                "message": "Bankruptcy not needed — workload is manageable",
            }

        # Mark sacrificed tasks as bankrupt
        sacrifice_titles = assessment.get("sacrifice_tasks", [])
        active_tasks = self._task_service.list_active_tasks(user_id)
        bankrupted_ids = []

        for task in active_tasks:
            if task.title in sacrifice_titles:
                try:
                    self._task_repo.mark_bankrupt(task.id)
                    bankrupted_ids.append(task.id)
                except Exception as exc:
                    logger.warning(
                        "Could not mark task as bankrupt",
                        task_id=task.id,
                        error=str(exc),
                    )

        # Store bankruptcy record
        now = datetime.now(timezone.utc).isoformat()
        bankruptcy_record = {
            "id": str(uuid4()),
            "userId": user_id,
            "declaredAt": now,
            "allTaskIds": [t.id for t in active_tasks],
            "prioritizedTaskIds": [
                t.id for t in active_tasks
                if t.title in assessment.get("prioritize_tasks", [])
            ],
            "sacrificedTaskIds": bankrupted_ids,
            "rationale": assessment.get("rationale", ""),
            "recoveryPlan": assessment.get("workload_reduction", ""),
            "resolved": False,
            "resolvedAt": None,
        }

        try:
            from app.core.firebase import get_firestore
            db = get_firestore()
            db.collection("bankruptcies").document(
                bankruptcy_record["id"]
            ).set(bankruptcy_record)
        except Exception as exc:
            logger.error("Could not store bankruptcy record", error=str(exc))

        logger.info(
            "Task bankruptcy declared",
            user_id=user_id,
            sacrificed=len(bankrupted_ids),
            kept=len(active_tasks) - len(bankrupted_ids),
        )

        # Record in memory
        try:
            from app.memory.short_term import ShortTermMemory
            stm = ShortTermMemory()
            stm.record(
                user_id=user_id,
                observation_type="bankruptcy_declared",
                data={
                    "sacrificed_count": len(bankrupted_ids),
                    "total_tasks": len(active_tasks),
                },
            )
        except Exception:
            pass

        return {
            "declared": True,
            "bankruptcy_id": bankruptcy_record["id"],
            "sacrificed_tasks": sacrifice_titles,
            "prioritized_tasks": assessment.get("prioritize_tasks", []),
            "focus_task": assessment.get("focus_task", ""),
            "rationale": assessment.get("rationale", ""),
            "message": f"Task Bankruptcy declared. {len(bankrupted_ids)} tasks deferred.",
        }