import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Organization,
    OrganizationCreate,
    OrganizationPublic,
    OrganizationUpdate,
    Message,
)

router = APIRouter()


@router.post("/", response_model=OrganizationPublic)
def create_organization(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    organization_in: OrganizationCreate,
) -> Any:
    """
    Create a new organization.
    Only team members without an organization can create one.
    """
    # Check user is a team member
    if getattr(current_user, "user_type", None) != "team_member":
        raise HTTPException(
            status_code=403,
            detail="Only team members can create organizations",
        )
    
    # Check user doesn't already have an organization
    if current_user.organization_id:
        raise HTTPException(
            status_code=400,
            detail="You already belong to an organization",
        )
    
    # Create the organization
    organization = crud.create_organization(
        session=session, organization_in=organization_in
    )
    
    # Assign the user to the new organization
    current_user.organization_id = organization.id
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    return organization


@router.get("/{organization_id}", response_model=OrganizationPublic)
def read_organization(
    session: SessionDep, current_user: CurrentUser, organization_id: uuid.UUID
) -> Any:
    """
    Get organization by ID.
    Users can only view their own organization.
    """
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Only allow viewing own organization (unless superuser)
    if not current_user.is_superuser and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )
    
    return organization


@router.put("/{organization_id}", response_model=OrganizationPublic)
def update_organization(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    organization_id: uuid.UUID,
    organization_in: OrganizationUpdate,
) -> Any:
    """
    Update an organization.
    Only team members from that organization can update it.
    """
    organization = session.get(Organization, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Only allow updating own organization (unless superuser)
    if not current_user.is_superuser and current_user.organization_id != organization_id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )
    
    update_dict = organization_in.model_dump(exclude_unset=True)
    organization.sqlmodel_update(update_dict)
    session.add(organization)
    session.commit()
    session.refresh(organization)
    
    return organization

