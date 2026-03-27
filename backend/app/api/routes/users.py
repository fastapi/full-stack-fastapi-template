import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_user_manager,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    AuditAction,
    AuditLogsPublic,
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UserRole,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_user_manager)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = (
        select(User).order_by(col(User.created_at).desc()).offset(skip).limit(limit)
    )
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_user_manager)],
    response_model=UserPublic,
)
def create_user(
    *, session: SessionDep, user_in: UserCreate, current_user: CurrentUser
) -> Any:
    """
    Create new user. Requires email and role at minimum.
    Password is optional (generated automatically for passwordless flow).
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email,
            username=user_in.email,
            password=user_in.password or "",
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    crud.create_audit_log(
        session=session,
        action=AuditAction.created,
        target_user_id=user.id,
        performed_by_id=current_user.id,
        changes=f"User created with role={user_in.role.value}",
    )
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    verified, _ = verify_password(body.current_password, current_user.hashed_password)
    if not verified:
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    return user


@router.get(
    "/audit-log",
    dependencies=[Depends(get_current_user_manager)],
    response_model=AuditLogsPublic,
)
def read_audit_logs(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve user audit logs.
    """
    logs, count = crud.get_audit_logs(session=session, skip=skip, limit=limit)
    return AuditLogsPublic(data=logs, count=count)


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
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
    "/{user_id}",
    dependencies=[Depends(get_current_user_manager)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: CurrentUser,
) -> Any:
    """
    Update a user (role, active status, etc.).
    """

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    changes_parts = []
    user_data = user_in.model_dump(exclude_unset=True)
    if "role" in user_data and user_data["role"] is not None:
        changes_parts.append(f"role: {db_user.role.value} -> {user_data['role']}")
    if "is_active" in user_data and user_data["is_active"] is not None:
        changes_parts.append(
            f"is_active: {db_user.is_active} -> {user_data['is_active']}"
        )
    if "email" in user_data and user_data["email"] is not None:
        changes_parts.append(f"email: {db_user.email} -> {user_data['email']}")
    if "full_name" in user_data:
        changes_parts.append(
            f"full_name: {db_user.full_name} -> {user_data['full_name']}"
        )

    is_deactivation = (
        "is_active" in user_data
        and user_data["is_active"] is False
        and db_user.is_active is True
    )

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)

    audit_action = AuditAction.deactivated if is_deactivation else AuditAction.updated
    crud.create_audit_log(
        session=session,
        action=audit_action,
        target_user_id=db_user.id,
        performed_by_id=current_user.id,
        changes="; ".join(changes_parts) if changes_parts else "No changes",
    )
    return db_user


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_user_manager)],
)
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user. Only a Super Admin can delete another Super Admin.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    if user.role == UserRole.super_admin and current_user.role != UserRole.super_admin:
        raise HTTPException(
            status_code=403,
            detail="Only a Super Admin can delete another Super Admin",
        )
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")
