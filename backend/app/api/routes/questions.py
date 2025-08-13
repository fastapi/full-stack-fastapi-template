import logging

from fastapi import APIRouter

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.core.openai import generate_questions_from_documents
from app.models import (
    GenerateQuestionsRequest,
    QuestionCreate,
    QuestionPublic,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("/generate", response_model=list[QuestionPublic])
async def generate_questions(
    *,
    session: SessionDep,
    payload: GenerateQuestionsRequest,
    current_user: CurrentUser,
) -> list[QuestionPublic]:
    # 1. Validate documents belong to user or are accessible

    # 2. Call your AI question generation function, passing document_ids or text
    generated_questions_texts = await generate_questions_from_documents(
        payload.document_ids
    )
    logger.info(f"Generated questions: {generated_questions_texts}")

    saved_questions = []
    for q_text in generated_questions_texts:
        question_create = QuestionCreate(question=q_text)
        db_question = crud.create_question(
            session=session,
            question_in=question_create,
            owner_id=current_user.id,
        )
        saved_questions.append(db_question)

    return saved_questions

    return saved_questions
