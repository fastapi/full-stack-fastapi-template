from celery import Celery
import os

from app.core.config import settings

# Get Redis connection details from environment variables
redis_server = os.environ.get("REDIS_SERVER", "localhost")
redis_port = os.environ.get("REDIS_PORT", "6379")
redis_url = f"redis://{redis_server}:{redis_port}/0"

# Get RabbitMQ connection details from environment variables
rabbitmq_user = os.environ.get("RABBITMQ_USER", "guest")
rabbitmq_password = os.environ.get("RABBITMQ_PASSWORD", "guest")
rabbitmq_server = os.environ.get("RABBITMQ_SERVER", "localhost")
broker_url = f"amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_server}:5672//"

celery_app = Celery(
    "worker",
    broker=broker_url,
    backend=redis_url,
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