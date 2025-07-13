#!/usr/bin/env python3
"""
Script to create a test counselor user for testing the counselor system.
"""

import uuid
from sqlmodel import Session, select
from app.core.db import engine
from app.core.security import get_password_hash
from app.models import User, Counselor, Organization


def create_test_counselor():
    """Create a test counselor user."""
    print("👩‍⚕️ Creating test counselor user...")
    
    with Session(engine) as session:
        # Check if test counselor already exists
        existing_user = session.exec(
            select(User).where(User.email == "test.counselor@example.com")
        ).first()
        
        if existing_user:
            print("✅ Test counselor user already exists")
            return
        
        # Get or create default organization
        default_org = session.exec(select(Organization)).first()
        if not default_org:
            print("🏢 Creating default organization...")
            default_org = Organization(
                name="Test Organization",
                description="Test organization for counselors",
                is_active=True
            )
            session.add(default_org)
            session.commit()
            session.refresh(default_org)
        
        # Create test counselor user
        test_user = User(
            email="test.counselor@example.com",
            full_name="Test Counselor",
            hashed_password=get_password_hash("testpassword123"),
            role="counselor",
            is_active=True,
            organization_id=default_org.id
        )
        session.add(test_user)
        session.commit()
        session.refresh(test_user)
        
        # Create counselor profile
        counselor = Counselor(
            user_id=test_user.id,
            organization_id=default_org.id,
            specializations="general counseling, crisis intervention, trauma therapy",
            license_number="TEST-COUNSELOR-001",
            license_type="Licensed Clinical Social Worker (LCSW)",
            is_available=True,
            max_concurrent_cases=15
        )
        session.add(counselor)
        session.commit()
        session.refresh(counselor)
        
        print("✅ Test counselor user created successfully!")
        print(f"   Email: {test_user.email}")
        print(f"   Password: testpassword123")
        print(f"   Role: {test_user.role}")
        print(f"   Counselor ID: {counselor.id}")
        print(f"   Organization: {default_org.name}")


if __name__ == "__main__":
    create_test_counselor() 