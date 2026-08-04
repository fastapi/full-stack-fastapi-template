import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.core.ai.openai import generate_questions_from_documents
from app.models import (
    Exam,
    ExamAttempt,
    ExamCreate,
    ExamPublic,
    ExamsPublic,
    ExamUpdate,
    GenerateQuestionsPublic,
    Message,
    QuestionCreate,
)

router = APIRouter(prefix="/exams", tags=["exams"])


@router.post("/generate", response_model=ExamPublic)
async def generate_exam(
    *,
    session: SessionDep,
    payload: GenerateQuestionsPublic,
    current_user: CurrentUser,
) -> ExamPublic:
    source_document_ids = [str(doc_id) for doc_id in payload.document_ids]

    exam_in = ExamCreate(
        title=payload.title,
        description="generated exam",
        duration_minutes=30,
        is_published=False,
        source_document_ids=source_document_ids,
        difficulty=payload.difficulty if payload.difficulty else None,
        question_types=payload.question_types if payload.question_types else [],
    )
    db_exam = crud.create_db_exam(
        session=session,
        exam_in=exam_in,
        owner_id=current_user.id,
        source_document_ids=source_document_ids,
    )

    # 2. Generate questions
    generated_questions: list[QuestionCreate] = await generate_questions_from_documents(
        session,
        payload.document_ids,
        num_questions=payload.num_questions if payload.num_questions else 5,
        difficulty=payload.difficulty if payload.difficulty else None,
        question_types=payload.question_types if payload.question_types else None,
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
    if exam.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.refresh(exam, attribute_names=["questions"])
    return exam


@router.get("/", response_model=ExamsPublic)
def read_exams(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve exams.
    """
    count_statement = (
        select(func.count()).select_from(Exam).where(Exam.owner_id == current_user.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Exam).where(Exam.owner_id == current_user.id).offset(skip).limit(limit)
    )
    exams = session.exec(statement).all()

    # Calculate highest score for each exam
    exam_publics = []
    for exam in exams:
        # Get the maximum score from all attempts for this exam
        max_score_statement: Any = (
            select(func.max(ExamAttempt.score))
            .where(ExamAttempt.exam_id == exam.id)
            .where(ExamAttempt.score.is_not(None))  # type: ignore[union-attr]
        )
        max_score = session.exec(max_score_statement).one_or_none()

        exam_dict = ExamPublic.model_validate(exam).model_dump()
        exam_dict["highest_score"] = float(max_score) if max_score is not None else None
        exam_publics.append(ExamPublic.model_validate(exam_dict))

    return ExamsPublic(data=exam_publics, count=count)


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
    if exam.owner_id != current_user.id:
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
    if exam.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(exam)
    session.commit()
    return Message(message="Exam deleted successfully")
