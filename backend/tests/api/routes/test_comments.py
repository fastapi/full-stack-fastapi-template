"""API route tests for comments"""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import (
    CommentCreate,
    OrganizationCreate,
    ProjectCreate,
    UserCreate,
)
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import random_email, random_lower_string


def create_test_team_member(
    client: TestClient, db: Session, org_id: uuid.UUID
) -> tuple[dict[str, str], uuid.UUID]:
    """Create a test team member user and return token headers and user_id"""
    user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(),
            password="password123",
            user_type="team_member",
            organization_id=org_id,
        ),
    )
    headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    return headers, user.id


def create_test_client(
    client: TestClient, db: Session, project_id: uuid.UUID
) -> tuple[dict[str, str], uuid.UUID]:
    """Create a test client user with access to a project"""
    user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(),
            password="password123",
            user_type="client",
        ),
    )
    # Grant access to project
    from app.models import ProjectAccessCreate

    crud.create_project_access(
        session=db,
        access_in=ProjectAccessCreate(
            project_id=project_id,
            user_id=user.id,
            role="viewer",
            can_comment=True,
            can_download=True,
        ),
    )
    headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )
    return headers, user.id


def test_create_comment_team_member(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating a comment as a team member"""
    # Setup: create org and project
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )

    # Create team member
    headers, _ = create_test_team_member(client, db, org.id)

    # Create comment
    data = {
        "project_id": str(project.id),
        "content": "This is a test comment",
    }
    r = client.post(
        f"{settings.API_V1_STR}/comments/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    comment = r.json()
    assert comment["content"] == "This is a test comment"
    assert comment["project_id"] == str(project.id)


def test_create_comment_client(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating a comment as a client"""
    # Setup: create org and project
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )

    # Create client with access
    headers, _ = create_test_client(client, db, project.id)

    # Create comment
    data = {
        "project_id": str(project.id),
        "content": "Client comment",
    }
    r = client.post(
        f"{settings.API_V1_STR}/comments/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    comment = r.json()
    assert comment["content"] == "Client comment"


def test_create_comment_no_access(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test that clients without access cannot comment"""
    # Setup: create org and project
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )

    # Create client WITHOUT access
    user = crud.create_user(
        session=db,
        user_create=UserCreate(
            email=random_email(),
            password="password123",
            user_type="client",
        ),
    )
    headers = authentication_token_from_email(
        client=client, email=user.email, db=db
    )

    # Try to create comment
    data = {
        "project_id": str(project.id),
        "content": "Unauthorized comment",
    }
    r = client.post(
        f"{settings.API_V1_STR}/comments/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 403
    assert "Access denied" in r.json()["detail"]


def test_get_project_comments(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test retrieving comments for a project"""
    # Setup: create org and project
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )

    # Create team member
    headers, user_id = create_test_team_member(client, db, org.id)

    # Create comments
    for i in range(3):
        comment_in = CommentCreate(
            project_id=project.id,
            content=f"Comment {i}",
        )
        crud.create_comment(session=db, comment_in=comment_in, user_id=user_id)

    # Get comments
    r = client.get(
        f"{settings.API_V1_STR}/comments/{project.id}",
        headers=headers,
    )

    assert r.status_code == 200
    comments = r.json()
    assert comments["count"] == 3
    assert len(comments["data"]) == 3
    # Verify user info is included
    assert "user" in comments["data"][0]


def test_delete_comment_author(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test that comment author can delete their comment"""
    # Setup: create org and project
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )

    # Create team member
    headers, user_id = create_test_team_member(client, db, org.id)

    # Create comment
    comment_in = CommentCreate(
        project_id=project.id,
        content="Comment to delete",
    )
    comment = crud.create_comment(session=db, comment_in=comment_in, user_id=user_id)

    # Delete comment
    r = client.delete(
        f"{settings.API_V1_STR}/comments/{comment.id}",
        headers=headers,
    )

    assert r.status_code == 200
    assert r.json()["message"] == "Comment deleted successfully"

    # Verify comment is deleted
    deleted_comment = crud.get_comment(session=db, comment_id=comment.id)
    assert deleted_comment is None


def test_delete_comment_not_author(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test that non-authors cannot delete comments"""
    # Setup: create org and project
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project",
            client_name="Test Client",
            organization_id=org.id,
        ),
    )

    # Create first user and comment
    headers1, user_id1 = create_test_team_member(client, db, org.id)
    comment_in = CommentCreate(
        project_id=project.id,
        content="Comment by user 1",
    )
    comment = crud.create_comment(session=db, comment_in=comment_in, user_id=user_id1)

    # Create second user
    headers2, _ = create_test_team_member(client, db, org.id)

    # Try to delete comment as second user
    r = client.delete(
        f"{settings.API_V1_STR}/comments/{comment.id}",
        headers=headers2,
    )

    assert r.status_code == 403
    assert "You can only delete your own comments" in r.json()["detail"]


def test_get_comments_project_not_found(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """Test getting comments for non-existent project"""
    # Create team member
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name=random_lower_string())
    )
    headers, _ = create_test_team_member(client, db, org.id)

    # Try to get comments for fake project
    fake_id = uuid.uuid4()
    r = client.get(
        f"{settings.API_V1_STR}/comments/{fake_id}",
        headers=headers,
    )

    assert r.status_code == 404
    assert "Project not found" in r.json()["detail"]

