"""
SPARK — PONR Worker
Background job that scans all active tasks for PONR status.
Triggered by Cloud Scheduler every 30 minutes.
"""

from app.core.logging import get_logger

logger = get_logger(__name__)


async def run_ponr_worker(user_id: str) -> dict:
    """Scans all active tasks for PONR crossings."""
    from app.services.ponr_service import PONRService

    ponr_service = PONRService()
    results = ponr_service.scan_all_for_user(user_id)

    ponr_passed = [r for r in results if r.ponr_passed]

    logger.info(
        "PONR worker completed",
        user_id=user_id,
        scanned=len(results),
        ponr_passed=len(ponr_passed),
    )

    return {
        "scanned": len(results),
        "ponr_passed_count": len(ponr_passed),
        "ponr_passed_tasks": [r.task_id for r in ponr_passed],
    }