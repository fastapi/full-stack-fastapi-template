from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import crud
from app.api import deps
from app.models import (
    Meeting,
    MeetingCreate,
    MeetingUpdate,
    MeetingPublic,
    MeetingsPublic,
)

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.get("", response_model=MeetingsPublic)
def read_meetings(
    *,
    session: Session = Depends(deps.get_session),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve meetings.
    """
    meetings, total = crud.meeting.get_meetings(
        session=session, skip=skip, limit=limit
    )
    return MeetingsPublic(data=meetings, count=total)


@router.post("", response_model=MeetingPublic)
def create_meeting(
    *,
    session: Session = Depends(deps.get_session),
    meeting_in: MeetingCreate,
) -> Any:
    """
    Create new meeting.
    """
    meeting = crud.meeting.create_meeting(session=session, meeting_in=meeting_in)
    return meeting


@router.get("/{meeting_id}", response_model=MeetingPublic)
def read_meeting(
    *,
    session: Session = Depends(deps.get_session),
    meeting_id: UUID,
) -> Any:
    """
    Get meeting by ID.
    """
    meeting = crud.meeting.get_meeting(session=session, meeting_id=meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.put("/{meeting_id}", response_model=MeetingPublic)
def update_meeting(
    *,
    session: Session = Depends(deps.get_session),
    meeting_id: UUID,
    meeting_in: MeetingUpdate,
) -> Any:
    """
    Update a meeting.
    """
    meeting = crud.meeting.get_meeting(session=session, meeting_id=meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    meeting = crud.meeting.update_meeting(
        session=session, db_obj=meeting, obj_in=meeting_in
    )
    return meeting


@router.delete("/{meeting_id}", response_model=MeetingPublic)
def delete_meeting(
    *,
    session: Session = Depends(deps.get_session),
    meeting_id: UUID,
) -> Any:
    """
    Delete a meeting.
    """
    meeting = crud.meeting.delete_meeting(session=session, meeting_id=meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting