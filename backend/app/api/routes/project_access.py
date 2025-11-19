import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message,
    ProjectAccessCreate,
    ProjectAccessInviteByEmail,
    ProjectAccessPublic,
    ProjectAccessUpdate,
    ProjectAccessWithUser,
    User,
)

router = APIRouter()


# AN - New endpoint to get all projects the current user has access to
@router.get("/my-projects")
def read_my_projects(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get all projects the current user has access to.
    For clients: returns projects they've been invited to.
    For team members: returns all projects in their organization.
    """
    if getattr(current_user, "user_type", None) == "client":
        # Use the existing function - perfect!
        projects = crud.get_user_accessible_projects(
            session=session, user_id=current_user.id, skip=0, limit=1000
        )
        return {"data": projects, "count": len(projects)}
    elif getattr(current_user, "user_type", None) == "team_member":
        if not current_user.organization_id:
            return {"data": [], "count": 0}
        projects = crud.get_projects_by_organization(
            session=session, 
            organization_id=current_user.organization_id, 
            skip=0, 
            limit=1000
        )
        return {"data": projects, "count": len(projects)}
    else:
        return {"data": [], "count": 0}

@router.post("/{project_id}/access/invite-by-email")
def invite_client_by_email(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
    invite_data: ProjectAccessInviteByEmail,
) -> Any:
    """
    Invite a client to a project by email.
    If user exists: grants immediate access
    If user doesn't exist: creates a pending invitation
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
    if (
        not current_user.organization_id
        or current_user.organization_id != project.organization_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to manage this project",
        )

    # Invite client by email
    try:
        access, is_pending = crud.invite_client_by_email(
            session=session,
            project_id=project_id,
            email=invite_data.email,
            role=invite_data.role,
            can_comment=invite_data.can_comment,
            can_download=invite_data.can_download,
        )

        if is_pending:
            return {
                "message": "Invitation sent. Client will get access when they sign up with this email.",
                "is_pending": True,
                "email": invite_data.email,
            }
        else:
            return {
                "message": "Client invited successfully",
                "is_pending": False,
                "access": ProjectAccessPublic.model_validate(access),
            }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
    DEPRECATED: Use /invite-by-email endpoint instead.
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
    if (
        not current_user.organization_id
        or current_user.organization_id != project.organization_id
    ):
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


@router.get("/{project_id}/access", response_model=list[ProjectAccessWithUser])
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
    # Convert to ProjectAccessWithUser
    result = []
    for access in access_list:
        user = session.get(User, access.user_id)
        if user:
            from app.models import UserPublic

            result.append(
                ProjectAccessWithUser(
                    id=access.id,
                    created_at=access.created_at,
                    project_id=access.project_id,
                    user_id=access.user_id,
                    role=access.role,
                    can_comment=access.can_comment,
                    can_download=access.can_download,
                    user=UserPublic.model_validate(user),
                )
            )
    return result


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
    crud.delete_project_access(session=session, project_id=project_id, user_id=user_id)
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


