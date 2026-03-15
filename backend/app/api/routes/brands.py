"""
Brands API routes for managing user brands.

Endpoints:
    GET /brands - Get list of brands for the current user
    GET /brands/{brand_id} - Get brand details with segments
    POST /brands/setup - Complete brand setup with segments and prompts
    PATCH /brands/{brand_id} - Update brand metadata
    PUT /brands/{brand_id} - Full update of brand with segments
    DELETE /brands/{brand_id} - Delete brand and its prompts
    POST /brands/{brand_id}/members - Add a member to the brand
    DELETE /brands/{brand_id}/members/{user_id} - Remove a member from the brand
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, delete, update
import logging
import uuid
from nanoid import generate as nanoid_generate

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.brands import (
    BrandResponse,
    BrandListResponse,
    BrandDetailResponse,
    BrandSetupRequest,
    BrandSetupResponse,
    BrandUpdateRequest,
    BrandUpdateResponse,
    BrandFullUpdateRequest,
    BrandMemberRequest,
    BrandMemberResponse,
    SegmentDetail,
)
from kila_models.models.database import (
    UsersTable,
    UsersProfileTable,
    BrandsTable,
    BrandPromptTable,
    BrandUserTable,
    UserSubscriptionTable,
)
from kila_models.models.base import ProjectRole, SubscriptionTier

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/brands", tags=["brands"])


def generate_id(prefix: str) -> str:
    return f"{prefix}{nanoid_generate(size=10)}"


async def _check_free_trial_active_brand_limit(user_id: str, db: AsyncSession, exclude_brand_id: str) -> None:
    """For free trial users: raise 403 if they already have another active brand."""
    sub_result = await db.execute(
        select(UserSubscriptionTable.tier).where(UserSubscriptionTable.user_id == user_id)
    )
    tier = sub_result.scalar_one_or_none()
    logger.info(f"[free-trial-check] user={user_id} tier={tier} exclude_brand={exclude_brand_id}")

    if tier != SubscriptionTier.free_trial:
        return  # pro users have no restriction

    # Count active brands owned by this user, excluding the one being edited
    count_result = await db.execute(
        select(func.count(BrandsTable.brand_id))
        .join(BrandUserTable, BrandUserTable.brand_id == BrandsTable.brand_id)
        .where(BrandUserTable.user_id == user_id)
        .where(BrandsTable.is_active == True)  # noqa: E712
        .where(BrandsTable.brand_id != exclude_brand_id)
    )
    other_active = count_result.scalar_one()
    logger.info(f"[free-trial-check] other_active_brands={other_active}")

    if other_active >= 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Free trial is limited to 1 active brand. Deactivate your current brand before activating another.",
        )


@router.get("", response_model=BrandListResponse)
async def get_brands(
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """Get all brands the current user owns or has monitor access to."""
    logger.info(f"Fetching brands for user: {current_user.user_id}")

    brand_user_query = select(BrandUserTable).where(
        BrandUserTable.user_id == current_user.user_id
    )
    bu_result = await db.execute(brand_user_query)
    brand_users = bu_result.scalars().all()

    if not brand_users:
        return BrandListResponse(brands=[], total_count=0)

    brand_ids = [bu.brand_id for bu in brand_users]

    brands_query = (
        select(BrandsTable)
        .where(BrandsTable.brand_id.in_(brand_ids))
        .order_by(desc(BrandsTable.created_datetime))
    )
    brands_result = await db.execute(brands_query)
    brands = brands_result.scalars().all()

    return BrandListResponse(
        brands=[
            BrandResponse(
                brand_id=b.brand_id,
                brand_name=b.brand_name,
                description=b.description,
                company_id=b.company_id,
                created_by=b.created_by,
                created_at=b.created_datetime,
                is_active=b.is_active,
            )
            for b in brands
        ],
        total_count=len(brands)
    )


@router.get("/{brand_id}", response_model=BrandDetailResponse)
async def get_brand_detail(
    brand_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """Get brand details including all segments."""
    # Verify access
    access_query = select(BrandUserTable).where(
        BrandUserTable.brand_id == brand_id,
        BrandUserTable.user_id == current_user.user_id
    )
    access_result = await db.execute(access_query)
    if not access_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Brand not found or access denied")

    brand_query = select(BrandsTable).where(BrandsTable.brand_id == brand_id)
    brand_result = await db.execute(brand_query)
    brand = brand_result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    prompts_query = (
        select(BrandPromptTable)
        .where(BrandPromptTable.brand_id == brand_id)
        .order_by(BrandPromptTable.id)
    )
    prompts_result = await db.execute(prompts_query)
    prompts = prompts_result.scalars().all()

    segments = [
        SegmentDetail(
            prompt_id=p.prompt_id,
            segment_name=p.segment or "",
            prompts=p.prompt,
            is_active=p.is_active,
        )
        for p in prompts
    ]

    return BrandDetailResponse(
        brand_id=brand.brand_id,
        brand_name=brand.brand_name,
        description=brand.description,
        company_id=brand.company_id,
        created_by=brand.created_by,
        created_at=brand.created_datetime,
        is_active=brand.is_active,
        segments=segments,
    )


@router.post("/setup", response_model=BrandSetupResponse, status_code=status.HTTP_201_CREATED)
async def setup_brand(
    setup_data: BrandSetupRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """Create a new brand with segments and prompts."""
    logger.info(f"Setting up brand for user: {current_user.user_id}, brand: {setup_data.brand_name}")

    try:
        # Get company_id from profile
        profile_query = select(UsersProfileTable).where(
            UsersProfileTable.user_id == current_user.user_id
        )
        profile_result = await db.execute(profile_query)
        user_profile = profile_result.scalar_one_or_none()
        company_id = (user_profile.company_id if user_profile else None) or f"company_{current_user.user_id}"

        # Enforce free trial quota: max 1 active brand
        await _check_free_trial_active_brand_limit(current_user.user_id, db, exclude_brand_id="")

        # Check for duplicate brand name for this user
        brand_name_lower = setup_data.brand_name.strip().lower()
        existing_query = select(BrandsTable).where(
            func.lower(BrandsTable.brand_name) == brand_name_lower,
            BrandsTable.created_by == current_user.user_id,
            BrandsTable.is_active == True
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'Brand "{setup_data.brand_name.strip()}" already exists. Please edit the existing brand instead.'
            )

        # Create brand
        brand_id = generate_id("B_")
        new_brand = BrandsTable(
            brand_id=brand_id,
            brand_name=setup_data.brand_name.strip(),
            description=setup_data.description,
            company_id=company_id,
            created_by=current_user.user_id,
            is_active=True,
        )
        db.add(new_brand)

        # Create brand-user relationship (OWNER)
        brand_user = BrandUserTable(
            brand_id=brand_id,
            user_id=current_user.user_id,
            user_role=ProjectRole.OWNER,
        )
        db.add(brand_user)

        # Create prompts for each segment
        prompt_count = 0
        for segment in setup_data.segments:
            if segment.segment_name.strip() and segment.prompts.strip():
                new_prompt = BrandPromptTable(
                    brand_id=brand_id,
                    brand_name=setup_data.brand_name.strip(),
                    prompt=segment.prompts.strip(),
                    prompt_id=str(uuid.uuid4()),
                    segment=segment.segment_name.strip(),
                    user_id=current_user.user_id,
                    company_id=company_id,
                    idempotency_key=str(uuid.uuid4()),
                    is_active=True,
                )
                db.add(new_prompt)
                prompt_count += 1

        await db.commit()
        logger.info(f"Brand setup completed: brand_id={brand_id}, prompts={prompt_count}")

        return BrandSetupResponse(brand_id=brand_id, prompt_count=prompt_count)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to setup brand: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to setup brand: {str(e)}")


@router.patch("/{brand_id}", response_model=BrandUpdateResponse)
async def update_brand(
    brand_id: str,
    update_data: BrandUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """Update brand metadata (name, description, is_active). Owner only."""
    logger.info(f"PATCH /brands/{brand_id} called, is_active={update_data.is_active}")
    try:
        # Verify OWNER access
        access_query = select(BrandUserTable).where(
            BrandUserTable.brand_id == brand_id,
            BrandUserTable.user_id == current_user.user_id,
            BrandUserTable.user_role == ProjectRole.OWNER,
        )
        access_result = await db.execute(access_query)
        if not access_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Brand not found or you don't have permission to update it")

        brand_query = select(BrandsTable).where(BrandsTable.brand_id == brand_id)
        brand_result = await db.execute(brand_query)
        brand = brand_result.scalar_one_or_none()
        if not brand:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

        if update_data.brand_name is not None:
            brand.brand_name = update_data.brand_name.strip()
        if update_data.description is not None:
            brand.description = update_data.description.strip() if update_data.description else None
        if update_data.is_active is not None:
            if update_data.is_active:
                await _check_free_trial_active_brand_limit(current_user.user_id, db, exclude_brand_id=brand_id)
            brand.is_active = update_data.is_active
            await db.execute(
                update(BrandPromptTable)
                .where(BrandPromptTable.brand_id == brand_id)
                .values(is_active=update_data.is_active)
            )

        await db.commit()
        return BrandUpdateResponse(brand_id=brand_id)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to update brand: {str(e)}")


@router.put("/{brand_id}", response_model=BrandSetupResponse)
async def update_brand_full(
    brand_id: str,
    update_data: BrandFullUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """Full update of brand: name, description, is_active, and all segments. Owner only."""
    logger.info(f"PUT /brands/{brand_id} called, is_active={update_data.is_active}")
    try:
        # Verify OWNER access
        access_query = select(BrandUserTable).where(
            BrandUserTable.brand_id == brand_id,
            BrandUserTable.user_id == current_user.user_id,
            BrandUserTable.user_role == ProjectRole.OWNER,
        )
        access_result = await db.execute(access_query)
        if not access_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Brand not found or you don't have permission to update it")

        brand_query = select(BrandsTable).where(BrandsTable.brand_id == brand_id)
        brand_result = await db.execute(brand_query)
        brand = brand_result.scalar_one_or_none()
        if not brand:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

        profile_query = select(UsersProfileTable).where(
            UsersProfileTable.user_id == current_user.user_id
        )
        profile_result = await db.execute(profile_query)
        user_profile = profile_result.scalar_one_or_none()
        company_id = (user_profile.company_id if user_profile else None) or f"company_{current_user.user_id}"

        if update_data.is_active:
            await _check_free_trial_active_brand_limit(current_user.user_id, db, exclude_brand_id=brand_id)

        brand.brand_name = update_data.brand_name.strip()
        brand.description = update_data.description
        brand.is_active = update_data.is_active

        # Replace all prompts
        await db.execute(delete(BrandPromptTable).where(BrandPromptTable.brand_id == brand_id))

        prompt_count = 0
        for segment in update_data.segments:
            if segment.segment_name.strip() and segment.prompts.strip():
                db.add(BrandPromptTable(
                    brand_id=brand_id,
                    brand_name=update_data.brand_name.strip(),
                    prompt=segment.prompts.strip(),
                    prompt_id=str(uuid.uuid4()),
                    segment=segment.segment_name.strip(),
                    user_id=current_user.user_id,
                    company_id=company_id,
                    idempotency_key=str(uuid.uuid4()),
                    is_active=update_data.is_active,
                ))
                prompt_count += 1

        await db.commit()
        return BrandSetupResponse(brand_id=brand_id, prompt_count=prompt_count,
                                  message="Brand updated successfully")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to update brand: {str(e)}")


@router.delete("/{brand_id}", response_model=BrandUpdateResponse)
async def delete_brand(
    brand_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """Delete a brand and all its prompts and member records. Owner only."""
    try:
        access_query = select(BrandUserTable).where(
            BrandUserTable.brand_id == brand_id,
            BrandUserTable.user_id == current_user.user_id,
            BrandUserTable.user_role == ProjectRole.OWNER,
        )
        access_result = await db.execute(access_query)
        if not access_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Brand not found or you don't have permission to delete it")

        deleted_prompts = await db.execute(
            delete(BrandPromptTable).where(BrandPromptTable.brand_id == brand_id)
        )
        await db.execute(delete(BrandUserTable).where(BrandUserTable.brand_id == brand_id))
        await db.execute(delete(BrandsTable).where(BrandsTable.brand_id == brand_id))
        await db.commit()

        logger.info(f"Brand {brand_id} deleted ({deleted_prompts.rowcount} prompts)")
        return BrandUpdateResponse(brand_id=brand_id, message=f"Brand deleted successfully ({deleted_prompts.rowcount} prompts removed)")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to delete brand: {str(e)}")


@router.post("/{brand_id}/members", response_model=BrandMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_brand_member(
    brand_id: str,
    member_data: BrandMemberRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """Add a member to the brand. Owner only."""
    try:
        # Verify requester is OWNER
        access_query = select(BrandUserTable).where(
            BrandUserTable.brand_id == brand_id,
            BrandUserTable.user_id == current_user.user_id,
            BrandUserTable.user_role == ProjectRole.OWNER,
        )
        access_result = await db.execute(access_query)
        if not access_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only brand owners can add members")

        role_value = member_data.user_role.lower()
        if role_value not in ("owner", "monitor"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="user_role must be 'owner' or 'monitor'")

        role = ProjectRole.OWNER if role_value == "owner" else ProjectRole.Monitor

        # Check if already a member
        existing_query = select(BrandUserTable).where(
            BrandUserTable.brand_id == brand_id,
            BrandUserTable.user_id == member_data.user_id,
        )
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="User is already a member of this brand")

        db.add(BrandUserTable(brand_id=brand_id, user_id=member_data.user_id, user_role=role))
        await db.commit()

        return BrandMemberResponse(brand_id=brand_id, user_id=member_data.user_id, user_role=role_value)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to add member: {str(e)}")


@router.delete("/{brand_id}/members/{user_id}", response_model=BrandUpdateResponse)
async def remove_brand_member(
    brand_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UsersTable = Depends(get_current_user)
):
    """Remove a member from the brand. Owner only (cannot remove self if last owner)."""
    try:
        access_query = select(BrandUserTable).where(
            BrandUserTable.brand_id == brand_id,
            BrandUserTable.user_id == current_user.user_id,
            BrandUserTable.user_role == ProjectRole.OWNER,
        )
        access_result = await db.execute(access_query)
        if not access_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Only brand owners can remove members")

        result = await db.execute(
            delete(BrandUserTable).where(
                BrandUserTable.brand_id == brand_id,
                BrandUserTable.user_id == user_id,
            )
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

        await db.commit()
        return BrandUpdateResponse(brand_id=brand_id, message="Member removed successfully")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to remove member: {str(e)}")
