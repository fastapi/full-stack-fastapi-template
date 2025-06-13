import uuid
from datetime import date
from typing import List, Optional
from sqlmodel import Session, select
from app.models import PersonalBest, PersonalBestCreate

# Tracked exercise mapping
TRACKED_EXERCISES = {
    "bench press": "bench-press",
    "squat": "squat",
    "deadlift": "deadlift",
    "push-ups": "pushups",
    "pull-ups": "pullups",
}

def create_or_update_personal_best(
    *, session: Session, user_id: uuid.UUID, pb_in: PersonalBestCreate
) -> PersonalBest:
    # see if user already has a PB on this metric
    stmt = select(PersonalBest).where(
        PersonalBest.user_id == user_id,
        PersonalBest.metric == pb_in.metric
    )
    existing = session.exec(stmt).one_or_none()

    # update if new value is "better" (you define the logic per metric)
    if existing:
        if pb_in.value > existing.value:
            existing.value = pb_in.value
            existing.date = pb_in.date
            session.add(existing)
    else:
        existing = PersonalBest.model_validate(pb_in, update={"user_id": user_id})
        session.add(existing)

    session.commit()
    session.refresh(existing)
    return existing

def get_personal_bests(
    *, session: Session, user_id: uuid.UUID
) -> list[PersonalBest]:
    stmt = select(PersonalBest).where(PersonalBest.user_id == user_id)
    return session.exec(stmt).all()

def get_personal_best(
    *, session: Session, user_id: uuid.UUID, metric: str
) -> PersonalBest | None:
    stmt = select(PersonalBest).where(
        PersonalBest.user_id == user_id,
        PersonalBest.metric == metric
    )
    return session.exec(stmt).one_or_none()