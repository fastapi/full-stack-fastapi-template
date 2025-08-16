import json
from uuid import UUID

import openai
from pydantic import ValidationError
from sqlalchemy import select
from sqlmodel import Session

from app.core.config import settings
from app.models import Document, QuestionCreate, QuestionType

openai.api_key = settings.OPENAI_API_KEY
SYSTEM_PROMPT = """
You are a question generator.
Return ONLY valid JSON (no explanations) in this format:
[
  {
    "question": "string",
    "answer": "string or null",
    "type": "multiple_choice" | "true_false" | "short_answer",
    "options": ["string", "string"] // omit or null for non-multiple choice
  }
]
"""


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

Return each question as a JSON object with:
- "question": the question text
- "answer": the correct answer
- "type": one of "multiple_choice", "true_false", "short_answer"
- "options": list of possible answers if type is multiple_choice, otherwise null

Document text:
{text}

Return a JSON array of questions.
"""


async def generate_questions_from_documents(
    session: Session, document_ids: list[UUID], num_questions: int = 5
) -> list[QuestionCreate]:
    """
    Sends document texts to OpenAI and returns a list of QuestionCreate objects
    ready to insert into the DB.
    """
    questions: list[QuestionCreate] = []

    document_texts = [
        extracted_text or ""
        for extracted_text in get_document_texts_from_db(session, document_ids)
    ]
    if not document_texts:
        return []

    prompt = generate_questions_prompt(
        "\n".join(document_texts), num_questions=num_questions
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )

        generated_text = response.choices[0].message.content or ""
        raw_questions = json.loads(generated_text)

        # Convert raw JSON into QuestionCreate, normalizing options
        for q in raw_questions:
            questions.append(
                QuestionCreate(
                    question=q["question"],
                    answer=q.get("answer"),
                    type=QuestionType(q["type"]),
                    options=q.get("options") or [],  # normalize None for DB
                )
            )
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Failed to parse or validate response: {e}")
        print(f"Raw output:\n{generated_text}")

    return questions
