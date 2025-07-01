from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import User, UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserPublic])
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return users


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(user_id: str, session: SessionDep) -> Any:
    """
    Get a specific user by id.
    """
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
