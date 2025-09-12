"""models.User management API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app import crud, models
from app.api.deps import (
    SessionDep,
    get_current_active_superuser,
)
from app.constants import (
    BAD_REQUEST_CODE,
    CONFLICT_CODE,
    FORBIDDEN_CODE,
    NOT_FOUND_CODE,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.email_utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
)
def read_users(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> models.UsersPublic:
    """Retrieve users."""
    count_statement = select(func.count()).select_from(models.User)
    count = session.exec(count_statement).one()

    statement = select(models.User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return models.UsersPublic(user_data=users, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
)
def create_user(
    *,
    session: SessionDep,
    user_in: models.UserCreate,
) -> models.UserPublic:
    """Create new user."""
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=BAD_REQUEST_CODE,
            detail="The user with this email already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)
    if not settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email,
            username=user_in.email,
            password=user_in.password,
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return models.UserPublic.model_validate(user)


@router.patch("/me")
def update_user_me(
    *,
    session: SessionDep,
    user_in: models.UserUpdateMe,
    current_user: models.User,
) -> models.UserPublic:
    """Update own user."""
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=CONFLICT_CODE,
                detail="models.User with this email already exists",
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return models.UserPublic.model_validate(current_user)


@router.patch("/me/password")
def update_password_me(
    *,
    session: SessionDep,
    body: models.UpdatePassword,
    current_user: models.User,
) -> models.Message:
    """Update own password."""
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=BAD_REQUEST_CODE, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=BAD_REQUEST_CODE,
            detail="New password cannot be the same as the current one",
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return models.Message(message="Password updated successfully")


@router.get("/me")
def read_user_me(current_user: models.User) -> models.UserPublic:
    """Get current user."""
    return models.UserPublic.model_validate(current_user)


@router.delete("/me")
def delete_user_me(
    session: SessionDep,
    current_user: models.User,
) -> models.Message:
    """Delete own user."""
    if current_user.is_superuser:
        raise HTTPException(
            status_code=FORBIDDEN_CODE,
            detail="Super users are not allowed to delete themselves",
        )
    session.delete(current_user)
    session.commit()
    return models.Message(message="models.User deleted successfully")


@router.post("/signup")
def register_user(
    session: SessionDep,
    user_in: models.UserRegister,
) -> models.UserPublic:
    """Create new user without the need to be logged in."""
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=BAD_REQUEST_CODE,
            detail="The user with this email already exists in the system",
        )
    user_create = models.UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    return models.UserPublic.model_validate(user)


@router.get("/{user_id}")
def read_user_by_id(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: models.User,
) -> models.UserPublic:
    """Get a specific user by id."""
    user = session.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=NOT_FOUND_CODE, detail="models.User not found")
    if user == current_user:
        return models.UserPublic.model_validate(user)
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=FORBIDDEN_CODE,
            detail="The user doesn't have enough privileges",
        )
    return models.UserPublic.model_validate(user)


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: models.UserUpdate,
) -> models.UserPublic:
    """Update a user."""
    db_user = session.get(models.User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=NOT_FOUND_CODE,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=CONFLICT_CODE,
                detail="models.User with this email already exists",
            )

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    return models.UserPublic.model_validate(db_user)


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep,
    current_user: models.User,
    user_id: uuid.UUID,
) -> models.Message:
    """Delete a user."""
    user = session.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=NOT_FOUND_CODE, detail="models.User not found")
    if user == current_user:
        raise HTTPException(
            status_code=FORBIDDEN_CODE,
            detail="Super users are not allowed to delete themselves",
        )
    statement = delete(models.Item).where(col(models.Item.owner_id) == user_id)  # noqa: WPS221
    session.execute(statement)  # type: ignore[deprecated]
    session.delete(user)
    session.commit()
    return models.Message(message="models.User deleted successfully")
