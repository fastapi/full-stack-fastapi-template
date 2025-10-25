"""Celery worker configuration for async task processing."""

from celery import Celery  # type: ignore[import-untyped]

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "curriculum_extractor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Singapore",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    task_soft_time_limit=540,  # Soft limit at 9 minutes
    worker_prefetch_multiplier=1,  # Fetch one task at a time
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
)

# Auto-discover tasks from tasks module
celery_app.autodiscover_tasks(["app.tasks"])

# Configure default queue
celery_app.conf.task_default_queue = "celery"
celery_app.conf.task_default_exchange = "celery"
celery_app.conf.task_default_routing_key = "celery"

# Optional: Configure task routes for different queues (disabled for now)
# celery_app.conf.task_routes = {
#     "app.tasks.extraction.*": {"queue": "extraction"},
#     "app.tasks.default.*": {"queue": "default"},
# }
