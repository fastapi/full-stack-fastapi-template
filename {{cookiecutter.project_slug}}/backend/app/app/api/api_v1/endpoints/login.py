from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.utilities import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    refresh_token_expires = timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    refresh_token = security.create_refresh_token(user.id, expires_delta=refresh_token_expires)
    crud.token.create(db=db, obj_in=refresh_token, user_obj=user)
    return {
        "access_token": security.create_access_token(user.id, expires_delta=access_token_expires),
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login/refresh-token", response_model=schemas.Token)
def refresh_token(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_refresh_user),
) -> Any:
    """
    Refresh tokens for future requests
    """
    access_token_expires = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    refresh_token_expires = timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS)
    refresh_token = security.create_refresh_token(current_user.id, expires_delta=refresh_token_expires)
    crud.token.create(db=db, obj_in=refresh_token, user_obj=current_user)
    access_token = security.create_access_token(current_user.id, expires_delta=access_token_expires)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login/revoke-token", response_model=schemas.Msg)
def revoke_token(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_refresh_user),
) -> Any:
    """
    Revoke a refresh token
    """
    return {"msg": "Token revoked"}


@router.post("/password-recovery/{email}", response_model=schemas.Msg)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery
    """
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="This user does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    send_reset_password_email(email_to=user.email, email=email, token=password_reset_token)
    return {"msg": "Password recovery email sent."}


@router.post("/reset-password", response_model=schemas.Msg)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="This user does not exist in the system.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully."}
