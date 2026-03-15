from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from nanoid import generate
from typing import Optional
import logging

from app.core.db import get_db
from app.api.deps import get_current_user
from app.models.profile import (
    ProfileSetupRequest,
    ProfileResponse,
    CompanyResponse,
    CompanySearchResult,
    SubscriptionResponse,
)
from kila_models.models import UsersTable, UsersProfileTable, CompaniesTable
from kila_models.models.database import UserSubscriptionTable
from kila_models.models.base import SubscriptionTier, SubscriptionStatus
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profile", tags=["profile"])


def generate_company_id() -> str:
    """Generate a unique company ID with C_ prefix"""
    return f"C_{generate(size=8)}"


@router.get("/me", response_model=Optional[ProfileResponse])
async def get_profile(
    current_user: UsersTable = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current user's profile.

    Returns the profile data if it exists, or null if not set up.
    """
    # Fetch user profile
    stmt = select(UsersProfileTable).where(UsersProfileTable.user_id == current_user.user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        return None

    # If profile has a company_id, fetch company details
    company = None
    if profile.company_id:
        company_stmt = select(CompaniesTable).where(CompaniesTable.company_id == profile.company_id)
        company_result = await db.execute(company_stmt)
        company_record = company_result.scalar_one_or_none()
        if company_record:
            company = CompanyResponse(
                company_id=company_record.company_id,
                company_name=company_record.company_name
            )

    # Fetch subscription and apply lazy expiry check
    sub_stmt = select(UserSubscriptionTable).where(UserSubscriptionTable.user_id == current_user.user_id)
    sub_result = await db.execute(sub_stmt)
    subscription_row = sub_result.scalar_one_or_none()

    subscription = None
    if subscription_row:
        if (
            subscription_row.tier == SubscriptionTier.free_trial
            and subscription_row.status == SubscriptionStatus.active
            and subscription_row.trial_expires_at
            and subscription_row.trial_expires_at < datetime.now(timezone.utc)
        ):
            subscription_row.status = SubscriptionStatus.expired
            await db.commit()
            await db.refresh(subscription_row)

        subscription = SubscriptionResponse.model_validate(subscription_row)

    return ProfileResponse(
        user_id=profile.user_id,
        first_name=profile.first_name,
        middle_name=profile.middle_name,
        last_name=profile.last_name,
        email=profile.email,
        phone=profile.phone,
        job_title=profile.job_title,
        company=company,
        subscription=subscription,
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )


@router.post("/setup", response_model=ProfileResponse)
async def setup_profile(
    profile_data: ProfileSetupRequest,
    current_user: UsersTable = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create or update the current user's profile.

    - **first_name**: User's first name (required)
    - **middle_name**: User's middle name (optional)
    - **last_name**: User's last name (required)
    - **phone**: User's phone number (optional)
    - **email**: User's email address (required)
    - **company_name**: Company name (required) - will create new company if doesn't exist
    - **job_title**: User's job title (optional)
    """
    # Look up company by name (case-insensitive)
    company_stmt = select(CompaniesTable).where(
        CompaniesTable.company_name.ilike(profile_data.company_name)
    )
    company_result = await db.execute(company_stmt)
    company = company_result.scalar_one_or_none()

    # If company doesn't exist, create it with C_ prefix ID
    if not company:
        company = CompaniesTable(
            company_id=generate_company_id(),
            company_name=profile_data.company_name,
            email=profile_data.email,
        )
        db.add(company)
        await db.flush()  # Get company_id without committing
        logger.info(f"Created new company: {company.company_name} (ID: {company.company_id})")

    # Check if user profile already exists
    profile_stmt = select(UsersProfileTable).where(UsersProfileTable.user_id == current_user.user_id)
    profile_result = await db.execute(profile_stmt)
    existing_profile = profile_result.scalar_one_or_none()

    # Use empty string instead of None for middle_name due to database constraint
    middle_name = profile_data.middle_name or ""

    if existing_profile:
        # Update existing profile
        existing_profile.first_name = profile_data.first_name
        existing_profile.middle_name = middle_name
        existing_profile.last_name = profile_data.last_name
        existing_profile.phone = profile_data.phone
        existing_profile.email = profile_data.email
        existing_profile.company_id = company.company_id
        existing_profile.job_title = profile_data.job_title
        profile = existing_profile
        logger.info(f"Updated profile for user: {current_user.user_id}")
    else:
        # Create new profile
        profile = UsersProfileTable(
            user_id=current_user.user_id,
            first_name=profile_data.first_name,
            middle_name=middle_name,
            last_name=profile_data.last_name,
            email=profile_data.email,
            phone=profile_data.phone,
            company_id=company.company_id,
            job_title=profile_data.job_title,
        )
        db.add(profile)
        logger.info(f"Created new profile for user: {current_user.user_id}")

    await db.commit()
    await db.refresh(profile)

    # Backfill company_id on subscription row (only if not already set)
    await db.execute(
        update(UserSubscriptionTable)
        .where(UserSubscriptionTable.user_id == current_user.user_id)
        .where(UserSubscriptionTable.company_id.is_(None))
        .values(company_id=company.company_id)
    )
    await db.commit()

    return ProfileResponse(
        user_id=profile.user_id,
        first_name=profile.first_name,
        middle_name=profile.middle_name,
        last_name=profile.last_name,
        email=profile.email,
        phone=profile.phone,
        job_title=profile.job_title,
        company=CompanyResponse(
            company_id=company.company_id,
            company_name=company.company_name
        ),
        created_at=profile.created_at,
        updated_at=profile.updated_at
    )


@router.get("/companies/search", response_model=list[CompanySearchResult])
async def search_companies(
    q: str = Query(..., min_length=1, description="Search query for company name"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db),
    _: UsersTable = Depends(get_current_user)  # Require authentication
):
    """
    Search for existing companies by name.

    Returns a list of companies matching the search query.
    Used for company autocomplete in the profile setup form.
    """
    # Search companies by name (case-insensitive, partial match)
    stmt = (
        select(CompaniesTable)
        .where(CompaniesTable.company_name.ilike(f"%{q}%"))
        .where(CompaniesTable.is_active == True)  # noqa: E712
        .order_by(CompaniesTable.company_name)
        .limit(limit)
    )
    result = await db.execute(stmt)
    companies = result.scalars().all()

    return [
        CompanySearchResult(
            company_id=c.company_id,
            company_name=c.company_name
        )
        for c in companies
    ]
