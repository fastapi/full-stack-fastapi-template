import logging

from fastapi import APIRouter

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.core.openai import generate_questions_from_documents
from app.models import (
    GenerateQuestionsRequest,
    Question,
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
) -> list[Question]:
    # 1. Validate documents belong to user or are accessible

    # 2. Call your AI question generation function, passing document_ids or text
    generated_questions = await generate_questions_from_documents(
        session, payload.document_ids
    )

    saved_questions = []
    for question_create in generated_questions:
        db_question = crud.create_question(
            session=session,
            question_in=question_create,
            owner_id=current_user.id,
        )
        saved_questions.append(db_question)
    try:
        return [QuestionPublic.model_validate(q) for q in saved_questions]
    except Exception as e:
        logger.error(
            f"Failed to generate questions: {e} Saved questions: {saved_questions}"
        )
        raise
