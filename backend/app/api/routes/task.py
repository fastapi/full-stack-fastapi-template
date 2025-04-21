from fastapi import APIRouter, HTTPException
from typing import Optional
from app.api.deps import SessionDep
from app.models import (
    Task,
    TaskPublic
)

router = APIRouter(
    prefix="/task",
    tags=["task"]
)

@router.get("/{id}", response_model=TaskPublic)
def read_task(id: Optional[int], session: SessionDep):
    task = session.get(Task, id)
    task = TaskPublic(
            id=task.id, 
            title=task.title, 
            description=task.description,
            difficulty=task.difficulty, 
            illumination_type=task.illumination_type, 
            category=task.category, 
            created_at=task.created_at
        )
    if not task:
        raise HTTPException(status_code=404, detail="No task found")
    return task
