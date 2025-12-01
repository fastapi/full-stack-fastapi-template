"""Unit tests for Comment CRUD operations"""

import uuid

from sqlmodel import Session

from app import crud
from app.models import (
    CommentCreate,
    OrganizationCreate,
    ProjectCreate,
    UserCreate,
)


def test_create_comment(db: Session) -> None:
    """Test creating a new comment"""
    # Setup: create org, project, and user
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Test Org")
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    user = crud.create_user(
        session=db,
        user_create=UserCreate(email="test@example.com", password="password123"),
    )

    # Create comment
    comment_in = CommentCreate(
        project_id=project.id,
        content="This is a test comment",
    )

    comment = crud.create_comment(
        session=db, comment_in=comment_in, user_id=user.id
    )

    assert comment.content == "This is a test comment"
    assert comment.project_id == project.id
    assert comment.user_id == user.id
    assert comment.id is not None
    assert comment.created_at is not None


def test_get_comments_by_project(db: Session) -> None:
    """Test retrieving comments for a project"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Test Org")
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    user = crud.create_user(
        session=db,
        user_create=UserCreate(email="test@example.com", password="password123"),
    )

    # Create multiple comments
    for i in range(3):
        comment_in = CommentCreate(
            project_id=project.id,
            content=f"Comment {i}",
        )
        crud.create_comment(session=db, comment_in=comment_in, user_id=user.id)

    # Retrieve comments
    comments = crud.get_comments_by_project(session=db, project_id=project.id)

    assert len(comments) == 3
    contents = [c.content for c in comments]
    assert "Comment 0" in contents
    assert "Comment 1" in contents
    assert "Comment 2" in contents


def test_count_comments_by_project(db: Session) -> None:
    """Test counting comments for a project"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Test Org")
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    user = crud.create_user(
        session=db,
        user_create=UserCreate(email="test@example.com", password="password123"),
    )

    # Initially should have 0 comments
    count = crud.count_comments_by_project(session=db, project_id=project.id)
    assert count == 0

    # Create 5 comments
    for i in range(5):
        comment_in = CommentCreate(
            project_id=project.id,
            content=f"Comment {i}",
        )
        crud.create_comment(session=db, comment_in=comment_in, user_id=user.id)

    # Should now have 5 comments
    count = crud.count_comments_by_project(session=db, project_id=project.id)
    assert count == 5


def test_get_comment(db: Session) -> None:
    """Test retrieving a single comment by ID"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Test Org")
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    user = crud.create_user(
        session=db,
        user_create=UserCreate(email="test@example.com", password="password123"),
    )

    # Create comment
    comment_in = CommentCreate(
        project_id=project.id,
        content="Test comment",
    )
    created_comment = crud.create_comment(
        session=db, comment_in=comment_in, user_id=user.id
    )

    # Retrieve comment
    retrieved_comment = crud.get_comment(
        session=db, comment_id=created_comment.id
    )

    assert retrieved_comment is not None
    assert retrieved_comment.id == created_comment.id
    assert retrieved_comment.content == "Test comment"


def test_get_comment_not_found(db: Session) -> None:
    """Test retrieving a comment that doesn't exist"""
    fake_id = uuid.uuid4()
    comment = crud.get_comment(session=db, comment_id=fake_id)

    assert comment is None


def test_delete_comment(db: Session) -> None:
    """Test deleting a comment"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Test Org")
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    user = crud.create_user(
        session=db,
        user_create=UserCreate(email="test@example.com", password="password123"),
    )

    # Create comment
    comment_in = CommentCreate(
        project_id=project.id,
        content="Comment to delete",
    )
    comment = crud.create_comment(session=db, comment_in=comment_in, user_id=user.id)
    comment_id = comment.id

    # Verify comment exists
    assert crud.get_comment(session=db, comment_id=comment_id) is not None

    # Delete comment
    crud.delete_comment(session=db, comment_id=comment_id)

    # Verify comment is deleted
    assert crud.get_comment(session=db, comment_id=comment_id) is None


def test_get_comments_by_project_pagination(db: Session) -> None:
    """Test pagination for get_comments_by_project"""
    # Setup
    org = crud.create_organization(
        session=db, organization_in=OrganizationCreate(name="Test Org")
    )
    project = crud.create_project(
        session=db,
        project_in=ProjectCreate(
            name="Test Project", client_name="Client", organization_id=org.id
        ),
    )
    user = crud.create_user(
        session=db,
        user_create=UserCreate(email="test@example.com", password="password123"),
    )

    # Create 10 comments
    for i in range(10):
        comment_in = CommentCreate(
            project_id=project.id,
            content=f"Comment {i}",
        )
        crud.create_comment(session=db, comment_in=comment_in, user_id=user.id)

    # Test pagination: skip=0, limit=5
    comments = crud.get_comments_by_project(
        session=db, project_id=project.id, skip=0, limit=5
    )
    assert len(comments) == 5

    # Test pagination: skip=5, limit=5
    comments = crud.get_comments_by_project(
        session=db, project_id=project.id, skip=5, limit=5
    )
    assert len(comments) == 5

    # Test pagination: skip=10, limit=5 (should return empty)
    comments = crud.get_comments_by_project(
        session=db, project_id=project.id, skip=10, limit=5
    )
    assert len(comments) == 0

