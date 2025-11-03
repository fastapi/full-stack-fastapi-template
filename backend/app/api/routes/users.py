import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
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


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.get("/clients", response_model=UsersPublic)
def read_clients(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve client users. Team members can access this to invite clients.
    """
    if getattr(current_user, "user_type", None) != "team_member":
        raise HTTPException(
            status_code=403,
            detail="Only team members can list clients",
        )

    count_statement = (
        select(func.count())
        .select_from(User)
        .where(User.user_type == "client")
    )
    count = session.exec(count_statement).one()

    statement = (
        select(User)
        .where(User.user_type == "client")
        .offset(skip)
        .limit(limit)
    )
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
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
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
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
    if not verify_password(body.current_password, current_user.hashed_password):
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
    Team members are assigned to an organization only if they were invited.
    """
    from sqlmodel import select

    from app.models import OrganizationInvitation

    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    user_create = UserCreate.model_validate(user_in)

    # Check if there's an invitation for this email (team members only)
    if user_create.user_type == "team_member":
        statement = select(OrganizationInvitation).where(
            OrganizationInvitation.email == user_create.email
        )
        invitation = session.exec(statement).first()

        if invitation:
            # Auto-assign to the invited organization
            user_create.organization_id = invitation.organization_id
            # Delete the invitation after use
            session.delete(invitation)
            session.commit()

    user = crud.create_user(session=session, user_create=user_create)
    return user


@router.get("/pending", response_model=UsersPublic)
def get_pending_users(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get users without an organization (pending approval).
    Accessible by team members to invite people to their organization.
    """
    if getattr(current_user, "user_type", None) != "team_member":
        raise HTTPException(status_code=403, detail="Only team members can invite users")

    from sqlmodel import select

    count_statement = (
        select(func.count())
        .select_from(User)
        .where(User.organization_id.is_(None))  # type: ignore[union-attr]
        .where(User.user_type == "team_member")
    )
    count = session.exec(count_statement).one()

    statement = (
        select(User)
        .where(User.organization_id.is_(None))  # type: ignore[union-attr]
        .where(User.user_type == "team_member")
        .offset(skip)
        .limit(limit)
    )
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.patch("/{user_id}/assign-organization", response_model=UserPublic)
def assign_user_to_organization(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    organization_id: uuid.UUID | None = None,
) -> Any:
    """
    Assign a user to an organization.
    Team members can assign users to their own organization.
    Superusers can assign to any organization.
    """
    if getattr(current_user, "user_type", None) != "team_member" and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Determine which organization to assign to
    if current_user.is_superuser and organization_id:
        # Superuser can specify any organization
        target_org_id = organization_id
    else:
        # Team members assign to their own organization
        if not current_user.organization_id:
            raise HTTPException(status_code=400, detail="You must be part of an organization to invite others")
        target_org_id = current_user.organization_id

    # Verify organization exists
    from app.models import Organization
    org = session.get(Organization, target_org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    user.organization_id = target_org_id
    session.add(user)
    session.commit()
    session.refresh(user)

    return user


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
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
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

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)  # type: ignore
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")
