from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.session import get_db
from app.core.security import get_current_active_user
from app.models import PersonalBestCreate, PersonalBestRead, PersonalBestsList, Workout
from app import crud

router = APIRouter(tags=["personal-bests"], prefix="/personal-bests")


@router.post("/", response_model=PersonalBestRead, status_code=status.HTTP_201_CREATED)
def record_personal_best(
    pb_in: PersonalBestCreate,
    session: Session = Depends(get_db),
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
    session: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Get all personal bests for the current user.
    """
    print("list_personal_bests called")
    all_pbs = crud.get_personal_bests(session=session, user_id=current_user.id)
    return {"data": all_pbs, "count": len(all_pbs)}


@router.get("/{metric}", response_model=PersonalBestRead)
def get_personal_best(
    metric: str,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Get the personal best for a specific metric.
    """
    pb = crud.get_personal_best(
        session=session, user_id=current_user.id, metric=metric
    )
    if not pb:
        raise HTTPException(status_code=404, detail="No personal best for that metric")
    return pb


@router.post("/update-from-workout", response_model=Dict[str, Any])
def update_from_workout(
    workout: Workout,
    session: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """
    Update personal bests based on a completed workout.
    """
    crud.update_personal_bests_after_workout(session=session, workout=workout)
    return {"status": "success", "message": "Personal bests updated"}
