# ─── app/scheduler.py ──────────────────────────────────────────────────────────

import random
import requests
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from sqlmodel import Session, select
from app.core.db import engine            # your SQLModel engine from db.py
from app.crudFuncs import (
    get_due_custom_reminders,
    mark_reminder_as_sent
)
from app.models import PushToken     # to fetch all tokens for daily quotes

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

# A small list of motivational quotes
QUOTES = [
    "Believe you can and you’re halfway there.",
    "Fall seven times, stand up eight.",
    "Your limitation—it’s only your imagination.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Success doesn’t just find you—you have to go out and get it.",
]


def send_expo_push(expo_token: str, title: str, body: str, data: dict = None):
    """
    Send a single push via Expo’s REST API.
    """
    message = {
        "to": expo_token,
        "sound": "default",
        "title": title,
        "body": body,
        "data": data or {},
    }
    resp = requests.post(
        EXPO_PUSH_URL,
        json=message,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )
    if resp.status_code != 200:
        print(
            f"[Scheduler] Failed to send push to {expo_token}: "
            f"{resp.status_code} → {resp.text}"
        )


def job_send_custom_reminders():
    """
    Runs every minute: finds all due reminders, sends them, and marks them as sent.
    """
    with Session(engine) as session:
        due_list = get_due_custom_reminders(session=session)
        for reminder in due_list:
            send_expo_push(
                reminder.expo_token,
                "⏰ Reminder",
                reminder.message,
                {"type": "custom_reminder", "reminder_id": str(reminder.id)},
            )
            mark_reminder_as_sent(session=session, reminder_id=reminder.id)
            print(f"[{datetime.now(timezone.utc)}] Sent reminder {reminder.id}")


def job_send_quote_of_the_day():
    """
    Runs once per day at 15:00 UTC: picks a random quote and sends it
    to every Expo token in push_tokens.
    """
    with Session(engine) as session:
        quote = random.choice(QUOTES)
        title = "🌟 Motivation of the Day 🌟"
        body = quote
        tokens = session.exec(select(PushToken)).all()
        for tok in tokens:
            send_expo_push(tok.expo_token, title, body, {"type": "daily_quote"})
        print(f"[{datetime.now(timezone.utc)}] Sent daily quote to {len(tokens)} users.")


def start_scheduler():
    """
    Initialize APScheduler (non-blocking).  
     - job_send_custom_reminders runs every minute
     - job_send_quote_of_the_day runs daily at 15:00 UTC
    """
    scheduler = BackgroundScheduler(timezone=timezone.utc)

    scheduler.add_job(
        job_send_custom_reminders,
        CronTrigger(minute="*"),
        id="custom_reminders",
        replace_existing=True,
    )

    scheduler.add_job(
        job_send_quote_of_the_day,
        CronTrigger(hour=15, minute=0),
        id="daily_quote",
        replace_existing=True,
    )

    scheduler.start()
    print(
        "Scheduler started: custom reminders (every minute), "
        "daily quote (15:00 UTC)"
    )
