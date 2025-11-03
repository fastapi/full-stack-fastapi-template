import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    ProjectAccessCreate,
    ProjectAccessesPublic,
    ProjectAccessPublic,
    ProjectAccessUpdate,
    User,
)

router = APIRouter()


@router.post("/{project_id}/access", response_model=ProjectAccessPublic)
def grant_project_access(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    role: str = "viewer",
    can_comment: bool = True,
    can_download: bool = True,
) -> Any:
    """
    Grant a user access to a project (invite a client).
    Only team members can invite clients.
    """
    # Check if current user is a team member
    if getattr(current_user, "user_type", None) != "team_member":
        raise HTTPException(
            status_code=403,
            detail="Only team members can invite clients to projects",
        )

    # Check if project exists and user has access to it
    project = crud.get_project(session=session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if current user's organization owns the project
    if not current_user.organization_id or current_user.organization_id != project.organization_id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to manage this project",
        )

    # Check if user to be invited exists
    user_to_invite = session.get(User, user_id)
    if not user_to_invite:
        raise HTTPException(status_code=404, detail="User not found")

    # Create access
    access_in = ProjectAccessCreate(
        project_id=project_id,
        user_id=user_id,
        role=role,
        can_comment=can_comment,
        can_download=can_download,
    )
    access = crud.create_project_access(session=session, access_in=access_in)
    return access


@router.get("/{project_id}/access", response_model=ProjectAccessesPublic)
def read_project_access_list(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
) -> Any:
    """
    Get list of users with access to a project.
    Only team members from the project's organization can see this.
    """
    # Check if project exists
    project = crud.get_project(session=session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check permissions
    if getattr(current_user, "user_type", None) == "team_member":
        if current_user.organization_id != project.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
    else:
        # Clients can only see their own access
        if not crud.user_has_project_access(
            session=session, project_id=project_id, user_id=current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")

    access_list = crud.get_project_access_list(session=session, project_id=project_id)
    return ProjectAccessesPublic(data=access_list, count=len(access_list))


@router.delete("/{project_id}/access/{user_id}", response_model=Message)
def revoke_project_access(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Any:
    """
    Revoke a user's access to a project.
    Only team members from the project's organization can do this.
    """
    # Check if current user is a team member
    if getattr(current_user, "user_type", None) != "team_member":
        raise HTTPException(
            status_code=403,
            detail="Only team members can revoke project access",
        )

    # Check if project exists
    project = crud.get_project(session=session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check permissions
    if current_user.organization_id != project.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Revoke access
    crud.delete_project_access(
        session=session, project_id=project_id, user_id=user_id
    )
    return Message(message="Access revoked successfully")


@router.patch("/{project_id}/access/{user_id}", response_model=ProjectAccessPublic)
def update_project_access_permissions(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    access_in: ProjectAccessUpdate,
) -> Any:
    """
    Update a user's project access permissions.
    Only team members from the project's organization can do this.
    """
    # Check if current user is a team member
    if getattr(current_user, "user_type", None) != "team_member":
        raise HTTPException(
            status_code=403,
            detail="Only team members can update project access",
        )

    # Check if project exists
    project = crud.get_project(session=session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check permissions
    if current_user.organization_id != project.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get existing access
    db_access = crud.get_project_access(
        session=session, project_id=project_id, user_id=user_id
    )
    if not db_access:
        raise HTTPException(status_code=404, detail="Access not found")

    # Update access
    access = crud.update_project_access(
        session=session, db_access=db_access, access_in=access_in
    )
    return access

