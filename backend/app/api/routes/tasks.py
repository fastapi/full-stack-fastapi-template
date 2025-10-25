"""API routes for Celery task management and testing."""

from typing import Any

from celery.result import AsyncResult  # type: ignore[import-untyped]
from fastapi import APIRouter, HTTPException

from app.tasks.default import health_check_task, test_task
from app.worker import celery_app

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/health-check", response_model=dict[str, Any])
def trigger_health_check() -> dict[str, Any]:
    """
    Trigger a health check task to verify Celery worker is functioning.

    Returns:
        Task ID and status
    """
    task = health_check_task.delay()
    return {
        "task_id": task.id,
        "status": "queued",
        "message": "Health check task queued successfully",
    }


@router.post("/test", response_model=dict[str, Any])
def trigger_test_task(duration: int = 5) -> dict[str, Any]:
    """
    Trigger a test task that simulates work.

    Args:
        duration: How many seconds the task should run (default: 5)

    Returns:
        Task ID and status
    """
    if duration < 1 or duration > 60:
        raise HTTPException(
            status_code=400,
            detail="Duration must be between 1 and 60 seconds",
        )

    task = test_task.delay(duration)
    return {
        "task_id": task.id,
        "status": "queued",
        "duration": duration,
        "message": f"Test task queued to run for {duration} seconds",
    }


@router.get("/status/{task_id}", response_model=dict[str, Any])
def get_task_status(task_id: str) -> dict[str, Any]:
    """
    Get the status of a Celery task.

    Args:
        task_id: The Celery task ID

    Returns:
        Task status and result (if completed)
    """
    task_result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task_result.status,
        "ready": task_result.ready(),
    }

    if task_result.successful():
        response["result"] = task_result.result
    elif task_result.failed():
        response["error"] = str(task_result.info)

    return response


@router.get("/inspect/stats", response_model=dict[str, Any])
def get_worker_stats() -> dict[str, Any]:
    """
    Get Celery worker statistics.

    Returns:
        Worker stats including active tasks, registered tasks, etc.
    """
    inspector = celery_app.control.inspect()

    return {
        "stats": inspector.stats(),
        "active_tasks": inspector.active(),
        "registered_tasks": inspector.registered(),
        "scheduled_tasks": inspector.scheduled(),
    }
