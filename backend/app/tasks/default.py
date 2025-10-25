"""Default Celery tasks for testing and general operations."""

import logging
import time
from typing import Any

from app.worker import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.default.health_check")  # type: ignore[misc]
def health_check_task(self: Any) -> dict[str, str]:
    """
    Simple health check task to verify Celery worker is functioning.

    Returns:
        dict with status and task_id
    """
    logger.info(f"Health check task started: {self.request.id}")
    return {
        "status": "healthy",
        "task_id": self.request.id,
        "message": "Celery worker is operational",
    }


@celery_app.task(bind=True, name="app.tasks.default.test_task")  # type: ignore[misc]
def test_task(self: Any, duration: int = 5) -> dict[str, Any]:
    """
    Test task that simulates work by sleeping.

    Args:
        duration: Number of seconds to sleep (default: 5)

    Returns:
        dict with task details
    """
    logger.info(f"Test task started: {self.request.id}, duration: {duration}s")

    # Simulate work
    for i in range(duration):
        time.sleep(1)
        logger.info(f"Task {self.request.id}: {i+1}/{duration} seconds elapsed")

    logger.info(f"Test task completed: {self.request.id}")

    return {
        "status": "completed",
        "task_id": self.request.id,
        "duration": duration,
        "message": f"Task completed after {duration} seconds",
    }
