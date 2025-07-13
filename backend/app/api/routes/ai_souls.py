from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import (
    CurrentActiveUser,
    CurrentTrainerOrAdmin,
    CurrentAdmin,
    SessionDep,
    get_user_role,
    UserRole,
)
from app.models import (
    AISoulEntity,
    AISoulEntityCreate,
    AISoulEntityPublic,
    AISoulEntityUpdate,
    AISoulEntityWithUserInteraction,
    UserAISoulInteraction,
)

router = APIRouter()


@router.post("/", response_model=AISoulEntityPublic)
def create_ai_soul(
    *,
    db: SessionDep,
    current_user: CurrentTrainerOrAdmin,
    ai_soul_create: AISoulEntityCreate,
) -> AISoulEntity:
    """
    Create a new AI soul.
    Only trainers and admins can create souls.
    """
    ai_soul = AISoulEntity(
        **ai_soul_create.dict(),
        user_id=current_user.id,
    )
    db.add(ai_soul)
    db.commit()
    db.refresh(ai_soul)
    return ai_soul


@router.get("/", response_model=list[AISoulEntityWithUserInteraction])
def get_ai_souls(
    *,
    db: SessionDep,
    current_user: CurrentActiveUser,
    skip: int = 0,
    limit: int = 100,
) -> list[AISoulEntityWithUserInteraction]:
    """
    Get all AI souls with role-based interaction counts.
    Regular users see their own interaction counts.
    Admins and counselors see global interaction counts.
    """
    statement = select(AISoulEntity).offset(skip).limit(limit)
    ai_souls = db.exec(statement).all()
    
    user_role = get_user_role(current_user)
    is_admin_or_counselor = user_role in [UserRole.ADMIN, UserRole.COUNSELOR]
    
    result = []
    for soul in ai_souls:
        if is_admin_or_counselor:
            # Show global interaction count for admins and counselors
            interaction_count = soul.interaction_count
        else:
            # Show user-specific interaction count for regular users
            user_interaction = db.exec(
                select(UserAISoulInteraction).where(
                    UserAISoulInteraction.user_id == current_user.id,
                    UserAISoulInteraction.ai_soul_id == soul.id
                )
            ).first()
            interaction_count = user_interaction.interaction_count if user_interaction else 0
        
        soul_response = AISoulEntityWithUserInteraction(
            id=soul.id,
            name=soul.name,
            description=soul.description,
            persona_type=soul.persona_type,
            specializations=soul.specializations,
            base_prompt=soul.base_prompt,
            is_active=soul.is_active,
            user_id=soul.user_id,
            created_at=soul.created_at,
            updated_at=soul.updated_at,
            last_used=soul.last_used,
            interaction_count=interaction_count
        )
        result.append(soul_response)
    
    return result


@router.get("/{ai_soul_id}", response_model=AISoulEntityWithUserInteraction)
def get_ai_soul(
    *,
    db: SessionDep,
    current_user: CurrentActiveUser,
    ai_soul_id: UUID,
) -> AISoulEntityWithUserInteraction:
    """
    Get a specific AI soul by ID with role-based interaction count.
    Regular users see their own interaction count.
    Admins and counselors see global interaction count.
    """
    ai_soul = db.get(AISoulEntity, ai_soul_id)
    if not ai_soul:
        raise HTTPException(status_code=404, detail="AI Soul Entity not found")
    
    user_role = get_user_role(current_user)
    is_admin_or_counselor = user_role in [UserRole.ADMIN, UserRole.COUNSELOR]
    
    if is_admin_or_counselor:
        # Show global interaction count for admins and counselors
        interaction_count = ai_soul.interaction_count
    else:
        # Show user-specific interaction count for regular users
        user_interaction = db.exec(
            select(UserAISoulInteraction).where(
                UserAISoulInteraction.user_id == current_user.id,
                UserAISoulInteraction.ai_soul_id == ai_soul.id
            )
        ).first()
        interaction_count = user_interaction.interaction_count if user_interaction else 0
    
    return AISoulEntityWithUserInteraction(
        id=ai_soul.id,
        name=ai_soul.name,
        description=ai_soul.description,
        persona_type=ai_soul.persona_type,
        specializations=ai_soul.specializations,
        base_prompt=ai_soul.base_prompt,
        is_active=ai_soul.is_active,
        user_id=ai_soul.user_id,
        created_at=ai_soul.created_at,
        updated_at=ai_soul.updated_at,
        last_used=ai_soul.last_used,
        interaction_count=interaction_count
    )


@router.put("/{ai_soul_id}", response_model=AISoulEntity)
def update_ai_soul(
    *,
    db: SessionDep,
    current_user: CurrentTrainerOrAdmin,
    ai_soul_id: UUID,
    ai_soul_update: AISoulEntityUpdate,
) -> AISoulEntity:
    """
    Update a specific AI soul.
    Only trainers and admins can update souls.
    """
    ai_soul = db.get(AISoulEntity, ai_soul_id)
    if not ai_soul:
        raise HTTPException(status_code=404, detail="AI Soul Entity not found")

    # Only allow admins to edit any soul, trainers can only edit their own
    user_role = get_user_role(current_user)
    if user_role == UserRole.TRAINER and ai_soul.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Update fields
    for field, value in ai_soul_update.dict(exclude_unset=True).items():
        if field != "user_id":  # Prevent changing the owner
            setattr(ai_soul, field, value)

    db.add(ai_soul)
    db.commit()
    db.refresh(ai_soul)
    return ai_soul


@router.delete("/{ai_soul_id}")
def delete_ai_soul(
    *,
    db: SessionDep,
    current_user: CurrentAdmin,
    ai_soul_id: UUID,
) -> None:
    """
    Delete a specific AI soul.
    Only admins can delete souls.
    """
    ai_soul = db.get(AISoulEntity, ai_soul_id)
    if not ai_soul:
        raise HTTPException(status_code=404, detail="AI Soul Entity not found")

    db.delete(ai_soul)
    db.commit()
