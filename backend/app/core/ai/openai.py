import logging
from uuid import UUID

from langchain_openai import ChatOpenAI
from pydantic import SecretStr, ValidationError
from sqlalchemy import select
from sqlmodel import Session

from app.core.config import settings
from app.models import Document, QuestionCreate, QuestionOutput, QuestionType

# Initialize logging
logger = logging.getLogger(__name__)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    max_completion_tokens=500,
    api_key=SecretStr(settings.OPENAI_API_KEY),
)

structured_llm = llm.with_structured_output(QuestionOutput)


def get_document_texts_from_db(session: Session, document_ids: list[UUID]) -> list[str]:
    try:
        stmt = select(Document.extracted_text).where(Document.id.in_(document_ids))  # type: ignore[attr-defined, call-overload]
        results = session.exec(stmt).all()
        document_texts: list[str] = [text for (text,) in results if text]
        if not document_texts:
            raise Exception("No documents found with the provided IDs")
        return document_texts
    except Exception as e:
        print(f"Failed to extract and chunk text for documents {document_ids}: {e}")
        return []


def generate_questions_prompt(text: str, num_questions: int = 5) -> str:
    return f"""
Generate {num_questions} questions from the following document text.

Each question must include:
- question: the question text
- answer: the correct answer (if known)
- type: one of "multiple_choice", "true_false", or "short_answer"
- options: list of options if type is "multiple_choice", otherwise leave empty.

Document text:
{text}
"""


def fetch_document_texts(session: Session, document_ids: list[UUID]) -> list[str]:
    """Fetch extracted texts for given document IDs."""
    try:
        stmt = select(Document.extracted_text).where(Document.id.in_(document_ids))  # type: ignore[attr-defined, call-overload]
        results = session.exec(stmt).all()
        texts = [text for (text,) in results if text]
        if not texts:
            logger.warning(f"No text found for document IDs: {document_ids}")
        return texts
    except Exception as e:
        logger.error(f"Failed to fetch document texts for {document_ids}: {e}")
        return []


def validate_and_convert_question_item(q) -> QuestionCreate | None:
    """Validate LLM question item and convert to QuestionCreate."""
    if not getattr(q, "question", None) or not getattr(q, "type", None):
        logger.warning(f"Skipping invalid question: {q}")
        return None

    return QuestionCreate(
        question=q.question,
        answer=getattr(q, "answer", None),
        type=QuestionType(q.type),
        options=getattr(q, "options", []) or [],
    )


def parse_llm_output(llm_output) -> list[QuestionCreate]:
    """Parse LLM structured output into QuestionCreate list."""
    questions: list[QuestionCreate] = []

    if not hasattr(llm_output, "questions") or not isinstance(
        llm_output.questions, list
    ):
        logger.error(f"LLM returned unexpected output: {llm_output}")
        return questions

    for q in llm_output.questions:
        qc = validate_and_convert_question_item(q)
        if qc:
            questions.append(qc)

    return questions


async def generate_questions_from_documents(
    session: Session, document_ids: list[UUID], num_questions: int = 5
) -> list[QuestionCreate]:
    """Main function: fetch documents, generate questions via LLM, and return QuestionCreate objects."""
    document_texts = fetch_document_texts(session, document_ids)
    if not document_texts:
        return []

    prompt = generate_questions_prompt(
        "\n".join(document_texts), num_questions=num_questions
    )

    try:
        llm_output = structured_llm.invoke(prompt)
        return parse_llm_output(llm_output)
    except ValidationError as ve:
        logger.error(f"Pydantic validation error: {ve}")
    except Exception as e:
        logger.error(f"Error generating questions from LLM: {e}")

    return []
