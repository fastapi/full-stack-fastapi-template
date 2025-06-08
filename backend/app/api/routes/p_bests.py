from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session

from app import crudFuncs as crud
from app.api.deps import SessionDep, CurrentUser
from app.models import PersonalBestCreate, PersonalBestPublic


router = APIRouter(tags=["personal-bests"], prefix="/personal-bests")

@router.post("/", response_model=PersonalBestPublic, status_code=status.HTTP_201_CREATED)
def record_personal_best(
    pb_in: PersonalBestCreate,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Record or update a personal best for the current user.
    """
    pb = crud.create_or_update_personal_best(
        session=session, user_id=current_user.id, pb_in=pb_in
    )
    return pb

@router.get("/", response_model=List[PersonalBestPublic])
def list_personal_bests(
    session: SessionDep,
    current_user: CurrentUser,
):
    all_pbs = crud.get_personal_bests(session=session, user_id=current_user.id)
    return all_pbs

@router.get("/{metric}", response_model=PersonalBestPublic)
def get_personal_best(
    metric: str,
    session: SessionDep,
    current_user: CurrentUser,
):
    pb = crud.get_personal_best(
        session=session, user_id=current_user.id, metric=metric
    )
    if not pb:
        raise HTTPException(status_code=404, detail="No personal best for that metric")
    return pb
