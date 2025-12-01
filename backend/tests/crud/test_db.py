"""Unit tests for database initialization"""

from sqlmodel import Session, select

from app import crud
from app.core.config import settings
from app.core.db import init_db
from app.models import Organization, User


def test_init_db_creates_superuser(db: Session) -> None:
    """Test that init_db creates the superuser if it doesn't exist"""
    # Clear any existing superuser
    existing_user = db.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if existing_user:
        db.delete(existing_user)
        db.commit()

    # Run init_db
    init_db(db)

    # Verify superuser was created
    user = db.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    assert user is not None
    assert user.email == settings.FIRST_SUPERUSER
    assert user.is_superuser is True
    assert user.organization_id is not None


def test_init_db_creates_organization(db: Session) -> None:
    """Test that init_db creates an organization for the superuser"""
    # Clear any existing superuser and organization
    existing_user = db.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if existing_user:
        org_id = existing_user.organization_id
        db.delete(existing_user)
        if org_id:
            org = db.get(Organization, org_id)
            if org:
                db.delete(org)
        db.commit()

    # Run init_db
    init_db(db)

    # Verify organization was created
    user = db.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    assert user is not None
    assert user.organization_id is not None

    organization = db.get(Organization, user.organization_id)
    assert organization is not None
    assert organization.name == "Admin Organization"


def test_init_db_does_not_duplicate_superuser(db: Session) -> None:
    """Test that init_db doesn't create duplicate superusers"""
    # Run init_db first time
    init_db(db)

    # Count existing superusers
    users_before = db.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).all()
    count_before = len(users_before)

    # Run init_db again
    init_db(db)

    # Count superusers after
    users_after = db.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).all()
    count_after = len(users_after)

    # Should have same count (no duplicates)
    assert count_after == count_before
    assert count_after == 1

