"""Unit tests for Dashboard Statistics"""
from datetime import date, timedelta
from sqlmodel import Session

from app import crud
from app.models import OrganizationCreate, ProjectCreate
from tests.utils.utils import random_lower_string


def test_dashboard_stats_empty_organization(db: Session) -> None:
    """Test dashboard stats for an organization with no projects"""
    org_in = OrganizationCreate(name=random_lower_string())
    organization = crud.create_organization(session=db, organization_in=org_in)
    
    stats = crud.get_dashboard_stats(session=db, organization_id=organization.id)
    
    assert stats.active_projects == 0
    assert stats.upcoming_deadlines == 0
    assert stats.team_members == 0
    assert stats.completed_this_month == 0


def test_dashboard_stats_active_projects(db: Session) -> None:
    """Test counting active projects (in_progress and review status)"""
    org = crud.create_organization(
        session=db,
        organization_in=OrganizationCreate(name=random_lower_string())
    )
    
    # Create projects with different statuses
    crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Project 1",
            client_name="Client 1",
            status="in_progress",
            organization_id=org.id
        )
    )
    crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Project 2",
            client_name="Client 2",
            status="review",
            organization_id=org.id
        )
    )
    crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Project 3",
            client_name="Client 3",
            status="planning",  # Not active
            organization_id=org.id
        )
    )
    crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Project 4",
            client_name="Client 4",
            status="completed",  # Not active
            organization_id=org.id
        )
    )
    
    stats = crud.get_dashboard_stats(session=db, organization_id=org.id)
    
    # Should count only in_progress and review
    assert stats.active_projects == 2


def test_dashboard_stats_upcoming_deadlines(db: Session) -> None:
    """Test counting upcoming deadlines (within next 14 days)"""
    org = crud.create_organization(
        session=db,
        organization_in=OrganizationCreate(name=random_lower_string())
    )
    
    today = date.today()
    
    # Project with deadline in 5 days - should count
    crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Project Soon",
            client_name="Client",
            status="in_progress",
            deadline=today + timedelta(days=5),
            organization_id=org.id
        )
    )
    
    # Project with deadline in 30 days - should NOT count (too far)
    crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Project Later",
            client_name="Client",
            status="in_progress",
            deadline=today + timedelta(days=30),
            organization_id=org.id
        )
    )
    
    # Completed project with deadline in 7 days - should NOT count (completed)
    crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Project Done",
            client_name="Client",
            status="completed",
            deadline=today + timedelta(days=7),
            organization_id=org.id
        )
    )
    
    stats = crud.get_dashboard_stats(session=db, organization_id=org.id)
    
    # Should only count the first project
    assert stats.upcoming_deadlines == 1


def test_dashboard_stats_completed_this_month(db: Session) -> None:
    """Test counting projects completed this month"""
    org = crud.create_organization(
        session=db,
        organization_in=OrganizationCreate(name=random_lower_string())
    )
    
    # Create completed projects
    project1 = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Completed Project",
            client_name="Client",
            status="completed",
            organization_id=org.id
        )
    )
    
    # Also create a non-completed project
    crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="In Progress Project",
            client_name="Client",
            status="in_progress",
            organization_id=org.id
        )
    )
    
    stats = crud.get_dashboard_stats(session=db, organization_id=org.id)
    
    # Should count only completed projects
    assert stats.completed_this_month >= 1  # At least the one we created

