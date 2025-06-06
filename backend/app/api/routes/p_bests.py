# TODO test PB dedicated router,  3 REST routes, 1 post & 2 gets  

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app import crud
from app.core.db import get_session
from app.core.security import get_current_active_user
from app.models import PersonalBestCreate, PersonalBestRead, PersonalBestsList

router = APIRouter(tags=["personal-bests"], prefix="/personal-bests")

@router.post("/", response_model=PersonalBestRead, status_code=status.HTTP_201_CREATED)
def record_personal_best(
    pb_in: PersonalBestCreate,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_active_user),
):
    """
    Record or update a personal best for the current user.
    """
    pb = crud.create_or_update_personal_best(
        session=session, user_id=current_user.id, pb_in=pb_in
    )
    return pb

@router.get("/", response_model=PersonalBestsList)
def list_personal_bests(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_active_user),
):
    all_pbs = crud.get_personal_bests(session=session, user_id=current_user.id)
    return {"data": all_pbs, "count": len(all_pbs)}

@router.get("/{metric}", response_model=PersonalBestRead)
def get_personal_best(
    metric: str,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_active_user),
):
    pb = crud.get_personal_best(
        session=session, user_id=current_user.id, metric=metric
    )
    if not pb:
        raise HTTPException(status_code=404, detail="No personal best for that metric")
    return pb
