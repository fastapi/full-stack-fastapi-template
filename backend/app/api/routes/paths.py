import uuid
from typing import Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Path, Step, PathCreate, PathResponse, StepCreate, User
)

router = APIRouter(prefix="/paths", tags=["paths"])

@router.get("/", response_model=list[PathResponse])
async def list_paths(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve paths with their steps.
    """
    paths = session.exec(
        select(Path)
        .where(Path.creator_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    return paths

@router.get("/{path_id}", response_model=PathResponse)
async def get_path(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    path_id: uuid.UUID,
) -> Any:
    """
    Get path by ID with all its steps.
    """
    path = session.get(Path, path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    if path.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return path

@router.post("/", response_model=PathResponse)
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
        step = Step(
            path_id=path.id,
            number=step_data.number,
            role_prompt=step_data.role_prompt,
            validation_prompt=step_data.validation_prompt,
            exposition=step_data.exposition,
        )
        session.add(step)
    
    session.commit()
    session.refresh(path)
    return path

@router.put("/{path_id}", response_model=PathResponse)
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

    # Update path attributes
    path.title = path_in.title
    path.path_summary = path_in.path_summary
    path.updated_at = datetime.utcnow()

    # Replace all steps
    session.query(Step).filter(Step.path_id == path_id).delete()
    
    # Create new steps
    for step_data in path_in.steps:
        step = Step(
            path_id=path_id,
            number=step_data.number,
            role_prompt=step_data.role_prompt,
            validation_prompt=step_data.validation_prompt,
            exposition=step_data.exposition,
        )
        session.add(step)

    session.add(path)
    session.commit()
    session.refresh(path)
    return path

@router.delete("/{path_id}")
async def delete_path(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    path_id: uuid.UUID,
) -> dict:
    """
    Delete a path and all its steps.
    """
    path = session.get(Path, path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Path not found")
    if path.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    session.delete(path)
    session.commit()
    return {"message": "Path deleted successfully"}