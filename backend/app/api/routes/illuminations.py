from fastapi import APIRouter, HTTPException
from app.api.deps import SessionDep
from app.models import (
    Task,
    IlluminationPublic,
    TaskPublic
)

router = APIRouter(
    prefix="/illuminations",
    tags=["illuminations"]
)

@router.get("/{illumination_type}", response_model=IlluminationPublic)
def read_by_illumination_type(illumination_type: str, session: SessionDep):
    tasks = session.query(Task).filter(Task.illumination_type == illumination_type).all()
    tasks = [TaskPublic(
            id=task.id, 
            title=task.title, 
            description=task.description,
            difficulty=task.difficulty, 
            illumination_type=task.illumination_type, 
            category=task.category, 
            created_at=task.created_at
        ) for task in tasks]

    if not tasks:
        raise HTTPException(status_code=404, detail="No illuminations found")
    return IlluminationPublic(illumination_type=illumination_type, tasks=tasks)
