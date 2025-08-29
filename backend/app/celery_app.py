from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    'workflow_app',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0',
    include=['app.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# 周期性任务调度
celery_app.conf.beat_schedule = {
    'check-scheduled-workflows': {
        'task': 'app.tasks.check_scheduled_workflows',
        'schedule': crontab(minute='*/1'),  # 每分钟检查一次
    },
}

# 任务模块将在阶段2创建
# from app.tasks import *