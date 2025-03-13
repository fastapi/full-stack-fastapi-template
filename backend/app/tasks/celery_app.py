from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER,
    backend=settings.CELERY_BROKER,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Define task routes to organize workers
celery_app.conf.task_routes = {
    "app.tasks.worker.scrape_social_media": "scraper-queue",
    "app.tasks.worker.analyze_social_data": "analysis-queue",
    "app.tasks.worker.generate_reports": "reporting-queue",
}

# Set a default result expiration time (in seconds)
celery_app.conf.result_expires = 60 * 60 * 24  # 1 day 