from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.utilities import (
    generate_password_reset_token,
    send_email_validation_email,
    verify_password_reset_token,
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
            detail="This username already exists in the system",
        )
    # Create user auth
    user_in = schemas.UserCreate(password=password, email=email, full_name=full_name)
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.put("/", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        check_user = crud.user.get_by_email(db, email=email)
        if check_user and check_user.email != current_user.email:
            raise HTTPException(
                status_code=400,
                detail="This username already exists in the system",
            )
        user_in.email = email
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


@router.post("/send-validation-email", response_model=schemas.Msg, status_code=201)
def send_validation_email(
    *,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Send validation email.
    """
    password_validation_token = generate_password_reset_token(email=current_user.email)
    data = schemas.EmailValidation(
        **{
            "email": current_user.email,
            "subject": "Validate your email address",
            "token": password_validation_token,
        }
    )
    # EmailValidation
    send_email_validation_email(data=data)
    return {"msg": "Password validation email sent. Check your email and respond."}


@router.post("/validate-email", response_model=schemas.Msg)
def validate_email(
    *,
    db: Session = Depends(deps.get_db),
    payload: dict = Body(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Reset password
    """
    # https://stackoverflow.com/a/65114346/295606
    email = verify_password_reset_token(payload["validation"])
    if not email or current_user.email != email:
        raise HTTPException(
            status_code=400,
            detail="Invalid token",
        )
    crud.user.validate_email(db=db, db_obj=current_user)
    return {"msg": "Email address validated successfully."}


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
