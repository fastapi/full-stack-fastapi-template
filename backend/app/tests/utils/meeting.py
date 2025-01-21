import random
import string

from sqlmodel import Session

from app import crud
from app.models import MeetingCreate


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def create_random_meeting(db: Session) -> None:
    title = random_lower_string()
    agenda = random_lower_string()
    meeting_in = MeetingCreate(title=title, agenda=agenda)
    return crud.meeting.create_meeting(session=db, meeting_in=meeting_in) 