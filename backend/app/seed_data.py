"""Seed script to add sample projects and galleries to the database"""
import logging
from datetime import date, datetime, timedelta
from sqlmodel import Session, select

from app.core.db import engine
from app.models import Organization, Project, Gallery, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_data() -> None:
    with Session(engine) as session:
        # Get the default organization
        organization = session.exec(
            select(Organization).where(Organization.name == "Default Organization")
        ).first()
        
        if not organization:
            logger.error("Default organization not found! Run init_db first.")
            return
        
        logger.info(f"Using organization: {organization.name}")
        
        # Check if we already have sample data
        existing_projects = session.exec(
            select(Project).where(Project.organization_id == organization.id)
        ).first()
        
        if existing_projects:
            logger.info("Sample data already exists. Skipping seed.")
            return
        
        # Create sample projects
        today = date.today()
        
        project1 = Project(
            name="Sarah & John Wedding Photography",
            client_name="Sarah Thompson",
            client_email="sarah@example.com",
            description="Full day wedding photography coverage including ceremony, reception, and portraits. Client wants natural, candid shots with some posed family photos.",
            status="in_progress",
            deadline=today + timedelta(days=7),
            start_date=today - timedelta(days=18),
            budget="$3,500",
            progress=65,
            organization_id=organization.id
        )
        session.add(project1)
        
        project2 = Project(
            name="Product Shoot - TechCorp",
            client_name="TechCorp Inc.",
            client_email="marketing@techcorp.com",
            description="Product photography for new smartphone lineup. Clean white background shots and lifestyle photography.",
            status="review",
            deadline=today + timedelta(days=4),
            start_date=today - timedelta(days=7),
            budget="$2,000",
            progress=90,
            organization_id=organization.id
        )
        session.add(project2)
        
        project3 = Project(
            name="Brand Photography - StartupX",
            client_name="StartupX",
            client_email="team@startupx.com",
            description="Corporate headshots and office culture photography for startup's website and marketing materials.",
            status="planning",
            deadline=today + timedelta(days=12),
            start_date=today,
            budget="$1,800",
            progress=15,
            organization_id=organization.id
        )
        session.add(project3)
        
        project4 = Project(
            name="Corporate Headshots - Law Firm",
            client_name="Smith & Associates",
            client_email="office@smithlaw.com",
            description="Professional headshots for 25 attorneys and staff members.",
            status="planning",
            deadline=today + timedelta(days=10),
            start_date=today + timedelta(days=2),
            budget="$1,250",
            progress=10,
            organization_id=organization.id
        )
        session.add(project4)
        
        project5 = Project(
            name="Restaurant Menu Photography",
            client_name="Bella Italia",
            client_email="chef@bellaitalia.com",
            description="Food photography for new seasonal menu. 30 dishes to be photographed.",
            status="completed",
            deadline=today - timedelta(days=8),
            start_date=today - timedelta(days=30),
            budget="$1,500",
            progress=100,
            organization_id=organization.id
        )
        session.add(project5)
        
        # Commit projects first so we have their IDs
        session.commit()
        session.refresh(project1)
        session.refresh(project2)
        session.refresh(project3)
        session.refresh(project5)
        
        logger.info("Created 5 sample projects")
        
        # Create sample galleries
        gallery1 = Gallery(
            name="Engagement Shoot",
            date=today - timedelta(days=10),
            photo_count=87,
            photographer="Alice Johnson",
            status="published",
            cover_image_url="https://images.unsplash.com/photo-1519741497674-611481863552?w=400&h=300&fit=crop",
            project_id=project1.id
        )
        session.add(gallery1)
        
        gallery2 = Gallery(
            name="Wedding Day - Ceremony",
            date=today - timedelta(days=3),
            photo_count=234,
            photographer="Alice Johnson",
            status="processing",
            cover_image_url="https://images.unsplash.com/photo-1606800052052-a08af7148866?w=400&h=300&fit=crop",
            project_id=project1.id
        )
        session.add(gallery2)
        
        gallery3 = Gallery(
            name="Wedding Day - Reception",
            date=today - timedelta(days=3),
            photo_count=198,
            photographer="Bob Smith",
            status="processing",
            cover_image_url="https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=400&h=300&fit=crop",
            project_id=project1.id
        )
        session.add(gallery3)
        
        gallery4 = Gallery(
            name="Smartphone Collection - White BG",
            date=today - timedelta(days=3),
            photo_count=52,
            photographer="Charlie Davis",
            status="published",
            cover_image_url="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=300&fit=crop",
            project_id=project2.id
        )
        session.add(gallery4)
        
        gallery5 = Gallery(
            name="Lifestyle Shots",
            date=today - timedelta(days=3),
            photo_count=48,
            photographer="Charlie Davis",
            status="published",
            cover_image_url="https://images.unsplash.com/photo-1556656793-08538906a9f8?w=400&h=300&fit=crop",
            project_id=project2.id
        )
        session.add(gallery5)
        
        gallery6 = Gallery(
            name="Mood Board & References",
            date=today,
            photo_count=15,
            photographer="Alice Johnson",
            status="draft",
            cover_image_url="https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=400&h=300&fit=crop",
            project_id=project3.id
        )
        session.add(gallery6)
        
        gallery7 = Gallery(
            name="Menu Items - Appetizers",
            date=today - timedelta(days=20),
            photo_count=45,
            photographer="David Lee",
            status="published",
            cover_image_url="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop",
            project_id=project5.id
        )
        session.add(gallery7)
        
        gallery8 = Gallery(
            name="Menu Items - Main Courses",
            date=today - timedelta(days=18),
            photo_count=52,
            photographer="David Lee",
            status="published",
            cover_image_url="https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop",
            project_id=project5.id
        )
        session.add(gallery8)
        
        session.commit()
        logger.info("Created 8 sample galleries")
        logger.info("Sample data seeding complete!")


def main() -> None:
    logger.info("Starting sample data seeding...")
    seed_data()
    logger.info("Done!")


if __name__ == "__main__":
    main()

