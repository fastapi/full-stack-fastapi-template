import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    OrganizationInvitation,
    OrganizationInvitationCreate,
    OrganizationInvitationPublic,
    OrganizationInvitationsPublic,
)

router = APIRouter()


@router.post("/", response_model=OrganizationInvitationPublic)
def create_invitation(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    invitation_in: OrganizationInvitationCreate,
) -> Any:
    """
    Create an organization invitation.
    Team members can invite people to their organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400,
            detail="You must be part of an organization to invite others",
        )

    # Check if invitation already exists
    statement = select(OrganizationInvitation).where(
        OrganizationInvitation.email == invitation_in.email,
        OrganizationInvitation.organization_id == current_user.organization_id,
    )
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="An invitation has already been sent to this email",
        )

    invitation = OrganizationInvitation(
        email=invitation_in.email,
        organization_id=current_user.organization_id,
    )
    session.add(invitation)
    session.commit()
    session.refresh(invitation)
    return invitation


@router.get("/", response_model=OrganizationInvitationsPublic)
def read_invitations(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve invitations for the current user's organization.
    """
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400,
            detail="You must be part of an organization",
        )

    count_statement = (
        select(func.count())
        .select_from(OrganizationInvitation)
        .where(OrganizationInvitation.organization_id == current_user.organization_id)
    )
    count = session.exec(count_statement).one()

    statement = (
        select(OrganizationInvitation)
        .where(OrganizationInvitation.organization_id == current_user.organization_id)
        .offset(skip)
        .limit(limit)
    )
    invitations = session.exec(statement).all()

    return OrganizationInvitationsPublic(data=invitations, count=count)


@router.delete("/{invitation_id}")
def delete_invitation(
    session: SessionDep, current_user: CurrentUser, invitation_id: uuid.UUID
) -> Any:
    """
    Delete an invitation.
    """
    invitation = session.get(OrganizationInvitation, invitation_id)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found")

    if invitation.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(invitation)
    session.commit()
    return {"message": "Invitation deleted"}
