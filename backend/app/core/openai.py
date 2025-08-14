from typing import cast
from uuid import UUID

import openai
from sqlalchemy import select
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlmodel import Session

from app.core.config import settings
from app.models import Document

openai.api_key = settings.OPENAI_API_KEY


def get_document_texts_from_db(session: Session, document_ids: list[UUID]) -> list[str]:
    try:
        # document_query = select(Document).where(
        #     cast(InstrumentedAttribute, Document.id).in_(document_ids)
        # )
        # db_documents = session.exec(document_query).all()
        # document_texts = [doc.extracted_text for doc in db_documents if doc.extracted_text]
        stmt = select(Document.extracted_text).where(
            cast(InstrumentedAttribute, Document.id).in_(document_ids)
        )
        document_texts: list[str] = [
            text for (text,) in session.exec(stmt).all() if text
        ]

        if not document_texts:
            raise Exception("No documents found with the provided IDs")
        return document_texts
    except Exception as e:
        print(f"Failed to extract and chunk text for documents {document_ids}: {e}")
        return []


async def generate_questions_from_documents(
    session: Session, document_ids: list[UUID]
) -> list[str]:
    """
    Sends document texts to OpenAI to generate practice questions.
    Returns a list of question strings.
    """
    questions: list[str] = []
    try:
        document_texts = [
            extracted_text or ""
            for extracted_text in get_document_texts_from_db(session, document_ids)
        ]
        if not document_texts:
            return []

        prompt = "Generate practice questions based on the following documents:\n\n"
        prompt += "\n\n---\n\n".join(document_texts)
        prompt += "\n\nPlease provide a list of questions."

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that creates exam questions.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        # The generated text from OpenAI
        generated_text = response.choices[0].message.content or ""

        # Naively split into questions by line breaks, you can parse better if needed
        questions = [q.strip() for q in generated_text.split("\n") if q.strip()]
        return questions
    except Exception as e:
        print(f"Failed to generate questions from documents {document_ids}: {e}")
    return questions
