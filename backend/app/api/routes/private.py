from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app import crud
from app.api.deps import SessionDep
from app.models import (
    UserCreate,
    UserPublic,
)

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False


@router.post("/users/", response_model=UserPublic)
def create_user(user_in: PrivateUserCreate, session: SessionDep) -> Any:
    """
    Create a new user.
    """

    user_create = UserCreate(
        email=user_in.email,
        full_name=user_in.full_name,
        password=user_in.password,
    )

    user = crud.create_user(session=session, user_create=user_create)
    return user
