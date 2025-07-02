from typing import Any

from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select, delete

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import User, UserPublic, UserCreate, UserUpdate, UsersPublic, Message, UserUpdateMe, UpdatePassword
from app.core.security import get_password_hash, verify_password
from app.core.auth.roles import ceo_role, manager_role

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=UsersPublic, dependencies=[Depends(manager_role)])
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users. (Manager+ only)
    """
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    count_statement = select(User)
    count = len(session.exec(count_statement).all())
    return UsersPublic(data=users, count=count)


@router.post("/", response_model=UserPublic, dependencies=[Depends(ceo_role)])
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user. (CEO only)
    """
    # Check if user exists
    statement = select(User).where(User.email == user_in.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create user
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """
    if user_in.email:
        statement = select(User).where(User.email == user_in.email)
        existing_user = session.exec(statement).first()
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
    statement = delete(User).where(User.id == current_user.id)
    session.exec(statement)
    session.commit()
    return Message(message="User deleted successfully")


@router.get("/{user_id}", response_model=UserPublic, dependencies=[Depends(manager_role)])
def read_user_by_id(user_id: str, session: SessionDep) -> Any:
    """
    Get a specific user by id. (Manager+ only)
    """
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserPublic, dependencies=[Depends(ceo_role)])
def update_user(
    *,
    session: SessionDep,
    user_id: str,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user. (CEO only)
    """
    statement = select(User).where(User.id == user_id)
    db_user = session.exec(statement).first()
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    if user_in.email:
        statement = select(User).where(User.email == user_in.email)
        existing_user = session.exec(statement).first()
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    user_data = user_in.model_dump(exclude_unset=True)
    if user_in.password:
        user_data["hashed_password"] = get_password_hash(user_in.password)
        del user_data["password"]
    
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/{user_id}", response_model=Message, dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: str
) -> Any:
    """
    Delete a user. (Superuser only)
    """
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    statement = delete(User).where(User.id == user_id)
    session.exec(statement)
    session.commit()
    return Message(message="User deleted successfully")
