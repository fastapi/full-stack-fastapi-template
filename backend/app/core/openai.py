import openai
from sqlalchemy import select
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine
from app.models import Document

openai.api_key = settings.OPENAI_API_KEY


def get_documents_from_db(document_ids: list[str]) -> list[Document]:
    try:
        with Session(engine) as session:
            document_query = select(Document).where(Document.id.in_(document_ids))
            documents = session.exec(document_query).all()
            if not documents:
                raise Exception("No documents found with the provided IDs")
    except Exception as e:
        print(f"Failed to extract and chunk text for documents {document_ids}: {e}")


async def generate_questions_from_documents(document_ids: list[str]) -> list[str]:
    """
    Sends document texts to OpenAI to generate practice questions.
    Returns a list of question strings.
    """
    questions = []
    try:
        document_texts = [
            doc.extracted_text for doc in get_documents_from_db(document_ids)
        ]
        prompt = "Generate practice questions based on the following documents:\n\n"
        prompt += "\n\n---\n\n".join(document_texts)
        prompt += "\n\nPlease provide a list of questions."

        response = await openai.ChatCompletion.acreate(
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
        generated_text = response.choices[0].message.content

        # Naively split into questions by line breaks, you can parse better if needed
        questions = [q.strip() for q in generated_text.split("\n") if q.strip()]
        return questions
    except Exception as e:
        print(f"Failed to generate questions from documents {document_ids}: {e}")
