import uuid
from typing import Any
from datetime import datetime

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select, func

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Path, Step, PathCreate, PathPublic, PathInList, PathsPublic,
    utc_now
)

router = APIRouter(prefix="/paths", tags=["paths"])

@router.get("/", response_model=PathsPublic)
async def list_paths(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve paths without loading steps.
    """
    # Get total count
    count_statement = (
        select(func.count())
        .select_from(Path)
        .where(Path.creator_id == current_user.id)
    )
    count = session.exec(count_statement).one()

    # Get paths without loading steps
    statement = (
        select(Path)
        .where(Path.creator_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    paths = session.exec(statement).all()
    
    # Convert to PathInList responses
    path_responses = [
        PathInList(
            id=path.id,
            title=path.title,
            path_summary=path.path_summary,
            created_at=path.created_at,
        )
        for path in paths
    ]
    
    return PathsPublic(data=path_responses, count=count)

@router.get("/{path_id}", response_model=PathPublic)
async def get_path(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    path_id: uuid.UUID,
) -> Any:
    """
    Get path by ID with all its steps.
    """
    # Use select to explicitly join with steps
    statement = (
        select(Path)
        .where(Path.id == path_id)
        .where(Path.creator_id == current_user.id)
    )
    path = session.exec(statement).first()
    
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")

    return path

@router.post("/", response_model=PathPublic)
async def create_path(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    path_in: PathCreate,
) -> Any:
    """
    Create a new path with its steps.
    """
    path = Path(
        creator_id=current_user.id,
        title=path_in.title,
        path_summary=path_in.path_summary,
    )
    session.add(path)
    session.flush()  # This assigns the ID to the path

    # Create steps with proper ordering
    for step_data in path_in.steps:
        # Convert YoutubeExposition to JSON if present
        exposition_json = None
        if step_data.exposition:
            exposition_json = step_data.exposition.model_dump_json()

        step = Step(
            path_id=path.id,
            number=step_data.number,
            role_prompt=step_data.role_prompt,
            validation_prompt=step_data.validation_prompt,
            exposition_json=exposition_json,
        )
        session.add(step)
    
    session.commit()
    session.refresh(path)
    return path

@router.put("/{path_id}", response_model=PathPublic)
async def update_path(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    path_id: uuid.UUID,
    path_in: PathCreate,
) -> Any:
    """
    Update a path and all its steps. Steps will be completely replaced.
    """
    path = session.get(Path, path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    if path.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Update path fields
    path.title = path_in.title
    path.path_summary = path_in.path_summary
    path.updated_at = utc_now()

    # Delete existing steps
    for step in path.steps:
        session.delete(step)
    
    # Create new steps
    for step_data in path_in.steps:
        # Convert YoutubeExposition to JSON if present
        exposition_json = None
        if step_data.exposition:
            exposition_json = step_data.exposition.model_dump_json()

        step = Step(
            path_id=path.id,
            number=step_data.number,
            role_prompt=step_data.role_prompt,
            validation_prompt=step_data.validation_prompt,
            exposition_json=exposition_json,
        )
        session.add(step)

    session.commit()
    session.refresh(path)
    return path

@router.delete("/{path_id}")
async def delete_path(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    path_id: uuid.UUID,
) -> Any:
    """
    Delete a path and all its steps.
    """
    path = session.get(Path, path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    if path.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(path)  # This will cascade delete steps due to relationship
    session.commit()
    return {"message": "Path deleted successfully"}