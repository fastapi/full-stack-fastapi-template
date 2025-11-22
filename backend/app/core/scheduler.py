from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.config import settings

scheduler = AsyncIOScheduler()

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        print("Scheduler started")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler shutdown")
