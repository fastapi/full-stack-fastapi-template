"""Unit tests for Project CRUD operations"""
from datetime import date, timedelta
from sqlmodel import Session

from app import crud
from app.models import OrganizationCreate, ProjectCreate, ProjectUpdate
from app.tests.utils.utils import random_lower_string


def test_create_project(db: Session) -> None:
    """Test creating a new project"""
    # First create an organization
    org_in = OrganizationCreate(
        name=random_lower_string(),
        description="Test organization"
    )
    organization = crud.create_organization(session=db, organization_in=org_in)
    
    # Create a project
    project_name = f"Test Project {random_lower_string()}"
    client_name = f"Client {random_lower_string()}"
    deadline = date.today() + timedelta(days=30)
    
    project_in = ProjectCreate(
        name=project_name,
        client_name=client_name,
        description="Test project description",
        status="planning",
        deadline=deadline,
        budget="$5,000",
        progress=0,
        organization_id=organization.id
    )
    
    project = crud.create_project(session=db, project_in=project_in)
    
    assert project.name == project_name
    assert project.client_name == client_name
    assert project.status == "planning"
    assert project.deadline == deadline
    assert project.budget == "$5,000"
    assert project.progress == 0
    assert project.organization_id == organization.id
    assert project.id is not None


def test_get_project(db: Session) -> None:
    """Test retrieving a project by ID"""
    # Create organization and project
    org_in = OrganizationCreate(name=random_lower_string())
    organization = crud.create_organization(session=db, organization_in=org_in)
    
    project_in = ProjectCreate(
        name="Test Project",
        client_name="Test Client",
        status="in_progress",
        progress=50,
        organization_id=organization.id
    )
    created_project = crud.create_project(session=db, project_in=project_in)
    
    # Retrieve the project
    retrieved_project = crud.get_project(session=db, project_id=created_project.id)
    
    assert retrieved_project is not None
    assert retrieved_project.id == created_project.id
    assert retrieved_project.name == "Test Project"
    assert retrieved_project.progress == 50


def test_update_project(db: Session) -> None:
    """Test updating a project"""
    # Create organization and project
    org_in = OrganizationCreate(name=random_lower_string())
    organization = crud.create_organization(session=db, organization_in=org_in)
    
    project_in = ProjectCreate(
        name="Original Name",
        client_name="Test Client",
        status="planning",
        progress=0,
        organization_id=organization.id
    )
    project = crud.create_project(session=db, project_in=project_in)
    
    # Update the project
    project_update = ProjectUpdate(
        name="Updated Name",
        status="in_progress",
        progress=75
    )
    
    updated_project = crud.update_project(
        session=db,
        db_project=project,
        project_in=project_update
    )
    
    assert updated_project.name == "Updated Name"
    assert updated_project.status == "in_progress"
    assert updated_project.progress == 75
    assert updated_project.client_name == "Test Client"  # Unchanged field


def test_get_projects_by_organization(db: Session) -> None:
    """Test retrieving all projects for an organization"""
    # Create organization
    org_in = OrganizationCreate(name=random_lower_string())
    organization = crud.create_organization(session=db, organization_in=org_in)
    
    # Create multiple projects
    project1 = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Project 1",
            client_name="Client 1",
            organization_id=organization.id
        )
    )
    
    project2 = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Project 2",
            client_name="Client 2",
            organization_id=organization.id
        )
    )
    
    # Retrieve projects
    projects = crud.get_projects_by_organization(
        session=db,
        organization_id=organization.id
    )
    
    assert len(projects) == 2
    project_names = [p.name for p in projects]
    assert "Project 1" in project_names
    assert "Project 2" in project_names


def test_count_projects_by_organization(db: Session) -> None:
    """Test counting projects for an organization"""
    # Create organization
    org_in = OrganizationCreate(name=random_lower_string())
    organization = crud.create_organization(session=db, organization_in=org_in)
    
    # Initially should have 0 projects
    count = crud.count_projects_by_organization(
        session=db,
        organization_id=organization.id
    )
    assert count == 0
    
    # Create 3 projects
    for i in range(3):
        crud.create_project(
            session=db,
            project_in=ProjectCreate(
                name=f"Project {i}",
                client_name=f"Client {i}",
                organization_id=organization.id
            )
        )
    
    # Should now have 3 projects
    count = crud.count_projects_by_organization(
        session=db,
        organization_id=organization.id
    )
    assert count == 3


def test_delete_project(db: Session) -> None:
    """Test deleting a project"""
    # Create organization and project
    org_in = OrganizationCreate(name=random_lower_string())
    organization = crud.create_organization(session=db, organization_in=org_in)
    
    project_in = ProjectCreate(
        name="Project to Delete",
        client_name="Test Client",
        organization_id=organization.id
    )
    project = crud.create_project(session=db, project_in=project_in)
    project_id = project.id
    
    # Verify project exists
    assert crud.get_project(session=db, project_id=project_id) is not None
    
    # Delete project
    crud.delete_project(session=db, project_id=project_id)
    
    # Verify project is deleted
    assert crud.get_project(session=db, project_id=project_id) is None


def test_project_progress_validation(db: Session) -> None:
    """Test that project progress is validated (0-100)"""
    org_in = OrganizationCreate(name=random_lower_string())
    organization = crud.create_organization(session=db, organization_in=org_in)
    
    # Valid progress values
    for progress_val in [0, 50, 100]:
        project_in = ProjectCreate(
            name=f"Project {progress_val}",
            client_name="Test Client",
            progress=progress_val,
            organization_id=organization.id
        )
        project = crud.create_project(session=db, project_in=project_in)
        assert project.progress == progress_val

