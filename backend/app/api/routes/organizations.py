from typing import Any
from fastapi import APIRouter, HTTPException
from sqlmodel import select, func

from app.api.deps import SessionDep, CurrentUser
from app.models import (
    Organization,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationPublic,
    OrganizationsPublic,
    Message,

)

router = APIRouter(prefix="/organizations", tags=["organizations"])



# GET /organizations → List all organizations

@router.get("/", response_model=OrganizationsPublic)
def read_organizations(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve organizations.
    - Superusers see all organizations.
    - Normal users see only the ones they own or belong to.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Organization)
        count = session.exec(count_statement).one()
        statement = select(Organization).offset(skip).limit(limit)
        organizations = session.exec(statement).all()
    else:
        # assuming each org has an 'owner_id' field similar to items
        count_statement = (
            select(func.count())
            .select_from(Organization)
            .where(Organization.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Organization)
            .where(Organization.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        organizations = session.exec(statement).all()

    return OrganizationsPublic(data=organizations, count=count)



# GET /organizations/{id} → Get a specific organization

@router.get("/{id}", response_model=OrganizationPublic)
def read_organization(
    session: SessionDep, current_user: CurrentUser, id: str
) -> Any:
    """
    Get organization by ID.
    """
    org = session.get(Organization, id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not current_user.is_superuser and (org.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return org



# POST /organizations → Create a new organization

@router.post("/", response_model=OrganizationPublic)
def create_organization(
    *, session: SessionDep, current_user: CurrentUser, org_in: OrganizationCreate
) -> Any:
    """
    Create a new organization.
    """
    db_org = Organization.model_validate(org_in, update={"owner_id": current_user.id})
    session.add(db_org)
    session.commit()
    session.refresh(db_org)
    return db_org



# PUT /organizations/{id} → Update an organization

@router.put("/{id}", response_model=OrganizationPublic)
def update_organization(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: str,
    org_in: OrganizationUpdate,
) -> Any:
    """
    Update an organization.
    """
    org = session.get(Organization, id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not current_user.is_superuser and (org.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    update_data = org_in.model_dump(exclude_unset=True)
    org.sqlmodel_update(update_data)
    session.add(org)
    session.commit()
    session.refresh(org)
    return org



# DELETE /organizations/{id} → Delete an organization

@router.delete("/{id}", response_model=Message)
def delete_organization(
    session: SessionDep, current_user: CurrentUser, id: str
) -> Message:
    """
    Delete an organization.
    """
    org = session.get(Organization, id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not current_user.is_superuser and (org.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    session.delete(org)
    session.commit()
    return Message(message="Organization deleted successfully")
