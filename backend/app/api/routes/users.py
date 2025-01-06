import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import (
    CurrentUser,
    UserServiceDep,
    get_current_active_superuser,
    get_current_user,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, user_service: UserServiceDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user_in.email:
        existing_user = user_service.repository.get_by_email(email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    update_data = user_in.model_dump(exclude_unset=True)
    user_service.repository.update(current_user, update=update_data)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, user_service: UserServiceDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    update_data = {"hashed_password": hashed_password}
    user_service.repository.update(current_user, update=update_data)
    return Message(message="Password updated successfully")


@router.delete("/me", response_model=Message)
def delete_user_me(user_service: UserServiceDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    user_service.repository.delete(id=current_user.id)
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(user_service: UserServiceDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = user_service.repository.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = user_service.create(user_create=user_create)
    return user


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, user_service: UserServiceDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = user_service.repository.get_by_email(email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = user_service.create(user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.get(
    "/",
    dependencies=[Depends(get_current_user)],
    response_model=UsersPublic,
)
def read_users(user_service: UserServiceDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    count = user_service.repository.count()
    users: list[User] = user_service.repository.get_all(skip=skip, limit=limit)

    return UsersPublic(data=users, count=count)


@router.get(
    "/{id}",
    response_model=UserPublic,
)
def read_user(
    id: uuid.UUID, user_service: UserServiceDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = user_service.repository.get_by_id(id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch(
    "/{id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    user_service: UserServiceDep,
    id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """

    user = user_service.repository.get_by_id(id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = user_service.repository.get_by_email(email=user_in.email)
        if existing_user and existing_user.id != id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    user = user_service.update(db_user=user, user_update=user_in)
    return user


@router.delete("/{id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    user_service: UserServiceDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = user_service.repository.get_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    user_service.repository.delete(id)
    return Message(message="User deleted successfully")
