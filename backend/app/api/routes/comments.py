import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    CommentCreate,
    CommentsPublic,
    CommentPublic,
    CommentWithUser,
    Message,
    UserPublic,
)

router = APIRouter()


@router.post("/", response_model=CommentPublic)
def create_comment(
    session: SessionDep,
    current_user: CurrentUser,
    comment_in: CommentCreate,
) -> Any:
    """
    Create a new comment on a project.
    Both team members and clients can comment.
    """
    # Check if project exists
    project = crud.get_project(session=session, project_id=comment_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if user has access to the project
    if getattr(current_user, "user_type", None) == "client":
        # Client must have access
        if not crud.user_has_project_access(
            session=session, project_id=comment_in.project_id, user_id=current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
    elif getattr(current_user, "user_type", None) == "team_member":
        # Team member must be in the same organization
        if current_user.organization_id != project.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")

    # Create the comment
    comment = crud.create_comment(
        session=session, comment_in=comment_in, user_id=current_user.id
    )
    return comment


@router.get("/{project_id}", response_model=CommentsPublic)
def read_project_comments(
    session: SessionDep,
    current_user: CurrentUser,
    project_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all comments for a project.
    """
    # Check if project exists
    project = crud.get_project(session=session, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if user has access
    if getattr(current_user, "user_type", None) == "client":
        if not crud.user_has_project_access(
            session=session, project_id=project_id, user_id=current_user.id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
    elif getattr(current_user, "user_type", None) == "team_member":
        if current_user.organization_id != project.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")

    # Get comments
    comments = crud.get_comments_by_project(
        session=session, project_id=project_id, skip=skip, limit=limit
    )
    
    # Attach user info to each comment
    from app.models import User
    
    comments_with_user = []
    for comment in comments:
        user = session.get(User, comment.user_id)  # ← Use User, not UserPublic
        if user:
            comment_dict = comment.model_dump()
            comment_dict["user"] = UserPublic.model_validate(user)  # Convert to UserPublic
            comments_with_user.append(CommentWithUser(**comment_dict))
    
    return CommentsPublic(data=comments_with_user, count=len(comments_with_user))


@router.delete("/{comment_id}", response_model=Message)
def delete_comment(
    session: SessionDep,
    current_user: CurrentUser,
    comment_id: uuid.UUID,
) -> Any:
    """
    Delete a comment. Only the comment author can delete it.
    """
    comment = crud.get_comment(session=session, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Only the author can delete their comment
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")

    crud.delete_comment(session=session, comment_id=comment_id)
    return Message(message="Comment deleted successfully")