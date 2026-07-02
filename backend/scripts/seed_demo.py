"""
SPARK — Demo Data Seeder
Creates realistic demo data for hackathon presentation.
Run: python scripts/seed_demo.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta, timezone


async def seed_demo():
    """Creates demo tasks that tell the SPARK story."""
    from app.core.config import get_settings
    from app.core.firebase import initialize_firebase
    from app.ai.vertex_client import initialize_vertex_ai
    from app.services.task_service import TaskService
    from app.models.task import CreateTaskRequest

    # Initialize
    initialize_firebase()
    initialize_vertex_ai()

    # Import agents to register them
    import app.agents  # noqa: F401

    task_service = TaskService()
    user_id = "dev-user-001"

    now = datetime.now(timezone.utc)

    demo_tasks = [
        CreateTaskRequest(
            title="Machine Learning Assignment — Neural Networks",
            description="Implement a CNN for image classification using PyTorch. Include training loop, evaluation metrics, and visualization of results.",
            category="academic",
            priority="critical",
            deadline=(now + timedelta(hours=36)).isoformat(),
            estimatedHours=8.0,
            complexity="high",
            tags=["ml", "pytorch", "assignment"],
        ),
        CreateTaskRequest(
            title="Project Proposal for Software Engineering",
            description="Write a 5-page proposal for the capstone project including problem statement, methodology, timeline, and tech stack.",
            category="academic",
            priority="high",
            deadline=(now + timedelta(days=3)).isoformat(),
            estimatedHours=6.0,
            complexity="medium",
            tags=["proposal", "capstone"],
        ),
        CreateTaskRequest(
            title="Weekly Team Standup Presentation",
            description="Prepare slides for Monday standup covering last week's progress, blockers, and this week's goals.",
            category="work",
            priority="medium",
            deadline=(now + timedelta(days=2)).isoformat(),
            estimatedHours=2.0,
            complexity="low",
            tags=["presentation", "weekly"],
        ),
        CreateTaskRequest(
            title="Research Paper Literature Review",
            description="Read and summarize 10 papers on transformer architectures for the literature review section of the thesis.",
            category="academic",
            priority="high",
            deadline=(now + timedelta(days=7)).isoformat(),
            estimatedHours=15.0,
            complexity="high",
            tags=["research", "thesis", "transformers"],
        ),
    ]

    print("🚀 Seeding demo data for SPARK...")
    print(f"   User: {user_id}")
    print(f"   Tasks to create: {len(demo_tasks)}")
    print()

    for i, req in enumerate(demo_tasks):
        try:
            print(f"   [{i+1}/{len(demo_tasks)}] Creating: {req.title}")
            task = await task_service.create_task(user_id, req)
            print(f"           ✅ Task created: {task.id}")
            print(f"           📋 Milestones: {task.progress.milestonesTotal}")
        except Exception as exc:
            print(f"           ❌ Failed: {exc}")
        print()

    print("✨ Demo data seeding complete!")
    print("   Open http://localhost:5173/dashboard to see results")


if __name__ == "__main__":
    asyncio.run(seed_demo())