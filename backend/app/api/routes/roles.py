import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    Message,
    Role,
    RoleCreate,
    RolePublic,
    RolesPublic,
    RoleUpdate,
    User,
    UserPublic,
)

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RolesPublic,
)
def read_roles(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve roles. Admin only.
    """
    count_statement = select(func.count()).select_from(Role)
    count = session.exec(count_statement).one()

    statement = select(Role).offset(skip).limit(limit)
    roles = session.exec(statement).all()

    return RolesPublic(
        data=[RolePublic.model_validate(role) for role in roles], count=count
    )


@router.get(
    "/{role_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RolePublic,
)
def read_role(session: SessionDep, role_id: uuid.UUID) -> Any:
    """
    Get role by ID. Admin only.
    """
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RolePublic,
)
def create_role(*, session: SessionDep, role_in: RoleCreate) -> Any:
    """
    Create new role. Admin only.
    """
    # Check if role already exists
    existing_role = crud.get_role_by_name(session=session, name=role_in.name)
    if existing_role:
        raise HTTPException(
            status_code=400,
            detail="A role with this name already exists",
        )

    role = crud.create_role(session=session, role_create=role_in)
    return role


@router.put(
    "/{role_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=RolePublic,
)
def update_role(
    *,
    session: SessionDep,
    role_id: uuid.UUID,
    role_in: RoleUpdate,
) -> Any:
    """
    Update a role. Admin only.
    """
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Check if new name conflicts with existing role
    if role_in.name and role_in.name != role.name:
        existing_role = crud.get_role_by_name(session=session, name=role_in.name)
        if existing_role:
            raise HTTPException(
                status_code=400,
                detail="A role with this name already exists",
            )

    update_dict = role_in.model_dump(exclude_unset=True)
    role.sqlmodel_update(update_dict)
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


@router.delete(
    "/{role_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_role(session: SessionDep, role_id: uuid.UUID) -> Message:
    """
    Delete a role. Admin only.
    """
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    session.delete(role)
    session.commit()
    return Message(message="Role deleted successfully")


@router.post(
    "/{role_id}/assign/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def assign_role_to_user(
    session: SessionDep,
    role_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Any:
    """
    Assign a role to a user. Admin only.
    """
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user = crud.assign_role_to_user(session=session, user=user, role=role)
    return user


@router.delete(
    "/{role_id}/remove/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def remove_role_from_user(
    session: SessionDep,
    role_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Any:
    """
    Remove a role from a user. Admin only.
    """
    role = session.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user = crud.remove_role_from_user(session=session, user=user, role=role)
    return user
