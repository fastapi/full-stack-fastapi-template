from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.core import security
from app.utilities import (
    send_new_account_email,
)

router = APIRouter()


@router.post("/", response_model=schemas.User)
def create_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(...),
    email: EmailStr = Body(...),
    full_name: str = Body(None),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = crud.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="This username is not available.",
        )
    # Create user auth
    user_in = schemas.UserCreate(password=password, email=email, full_name=full_name)
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.put("/", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update user.
    """
    if current_user.hashed_password:
        user = crud.user.authenticate(db, email=current_user.email, password=obj_in.original)
        if not obj_in.original or not user:
            raise HTTPException(status_code=400, detail="Unable to authenticate this update.")
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if obj_in.password is not None:
        user_in.password = obj_in.password
    if obj_in.full_name is not None:
        user_in.full_name = obj_in.full_name
    if obj_in.email is not None:
        check_user = crud.user.get_by_email(db, email=obj_in.email)
        if check_user and check_user.email != current_user.email:
            raise HTTPException(
                status_code=400,
                detail="This username is not available.",
            )
        user_in.email = obj_in.email
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/", response_model=schemas.User)
def read_user(
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/all", response_model=List[schemas.User])
def read_all_users(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all current users.
    """
    return crud.user.get_multi(db=db, skip=skip, limit=limit)


@router.post("/new-totp", response_model=schemas.NewTOTP)
def request_new_totp(
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Request new keys to enable TOTP on the user account.
    """
    obj_in = security.create_new_totp(label=current_user.email)
    # Remove the secret ...
    obj_in.secret = None
    return obj_in


@router.post("/toggle-state", response_model=schemas.Msg)
def toggle_state(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Toggle user state (moderator function)
    """
    response = crud.user.toggle_user_state(db=db, obj_in=user_in)
    if not response:
        raise HTTPException(
            status_code=400,
            detail="Invalid request.",
        )
    return {"msg": "User state toggled successfully."}


@router.post("/create", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user (moderator function).
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    if settings.EMAILS_ENABLED and user_in.email:
        send_new_account_email(email_to=user_in.email, username=user_in.email, password=user_in.password)
    return user


@router.get("/tester", response_model=schemas.Msg)
def test_endpoint() -> Any:
    """
    Test current endpoint.
    """
    return {"msg": "Message returned ok."}
