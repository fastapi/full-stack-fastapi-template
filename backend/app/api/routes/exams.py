import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.core.ai.openai import generate_questions_from_documents
from app.models import (
    Exam,
    ExamCreate,
    ExamPublic,
    ExamsPublic,
    ExamUpdate,
    GenerateQuestionsRequest,
    Message,
    QuestionCreate,
)

router = APIRouter(prefix="/exams", tags=["exams"])


@router.post("/generate", response_model=ExamPublic)
async def generate_exam(
    *,
    session: SessionDep,
    payload: GenerateQuestionsRequest,
    current_user: CurrentUser,
) -> ExamPublic:
    # TODO: fix the hardcoding here
    exam_in = ExamCreate(
        title="Midterm Exam",
        description="generated exam",
        duration_minutes=30,
        is_published=False,
    )
    db_exam = crud.create_db_exam(
        session=session, exam_in=exam_in, owner_id=current_user.id
    )

    # 2. Generate questions
    generated_questions: list[QuestionCreate] = await generate_questions_from_documents(
        session, payload.document_ids
    )

    return crud.create_exam(
        session=session,
        db_exam=db_exam,
        questions=generated_questions,
    )


@router.get("/{id}", response_model=ExamPublic)
def read_exam(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get exam by ID.
    """
    exam = session.get(Exam, id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    if not current_user.is_superuser and (exam.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return exam


@router.get("/", response_model=ExamsPublic)
def read_exams(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve exams.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Exam)
        count = session.exec(count_statement).one()
        statement = select(Exam).offset(skip).limit(limit)
        exams = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Exam)
            .where(Exam.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Exam)
            .where(Exam.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        exams = session.exec(statement).all()

    return ExamsPublic(data=exams, count=count)


@router.put("/{id}", response_model=ExamPublic)
def update_exam(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    exam_in: ExamUpdate,
) -> Any:
    """
    Update an exam.
    """
    exam = session.get(Exam, id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    if not current_user.is_superuser and (exam.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_dict = exam_in.model_dump(exclude_unset=True)
    exam.sqlmodel_update(update_dict)
    session.add(exam)
    session.commit()
    session.refresh(exam)
    return exam


@router.delete("/{id}")
def delete_exam(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an exam.
    """
    exam = session.get(Exam, id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    if not current_user.is_superuser and (exam.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(exam)
    session.commit()
    return Message(message="Exam deleted successfully")
