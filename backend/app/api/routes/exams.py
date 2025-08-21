from fastapi import APIRouter

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.core.ai.openai import generate_questions_from_documents
from app.models import ExamCreate, ExamPublic, GenerateQuestionsRequest, QuestionCreate

router = APIRouter(prefix="/exams", tags=["exams"])


@router.post("/generate", response_model=ExamPublic)
async def generate_exam(
    *,
    session: SessionDep,
    payload: GenerateQuestionsRequest,
    current_user: CurrentUser,
) -> ExamPublic:
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
