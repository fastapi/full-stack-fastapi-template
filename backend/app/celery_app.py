"""
Celery Application Configuration for AI Soul Entity Backend

This module configures Celery for background task processing including:
- Document processing and chunking
- Embedding generation
- RAG indexing operations
- Periodic cleanup tasks
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "ai_soul_entity",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.document_processing",
        "app.tasks.rag_tasks",
        "app.tasks.cleanup_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.tasks.document_processing.*": {"queue": "document_processing"},
        "app.tasks.rag_tasks.*": {"queue": "rag_processing"},
        "app.tasks.cleanup_tasks.*": {"queue": "cleanup"},
    },

    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution settings
    task_always_eager=False,
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_eager_result=True,

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,

    # Result backend settings
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },

    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-expired-sessions": {
            "task": "app.tasks.cleanup_tasks.cleanup_expired_sessions",
            "schedule": crontab(minute=0, hour=2),  # Daily at 2 AM
        },
        "cleanup-old-logs": {
            "task": "app.tasks.cleanup_tasks.cleanup_old_processing_logs",
            "schedule": crontab(minute=0, hour=3),  # Daily at 3 AM
        },
        "update-search-analytics": {
            "task": "app.tasks.rag_tasks.update_search_analytics",
            "schedule": crontab(minute=0, hour=1),  # Daily at 1 AM
        },
    },

    # Error handling
    task_reject_on_worker_lost=True,
    task_acks_late=True,

    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Auto-discover tasks
celery_app.autodiscover_tasks()

if __name__ == "__main__":
    celery_app.start()
