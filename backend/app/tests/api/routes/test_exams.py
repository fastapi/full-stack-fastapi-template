from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import QuestionCreate, QuestionType
from app.tests.utils.document import create_random_documents


def test_generate_exam(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test generating questions from documents using mocked OpenAI."""

    # Create some test documents
    documents = create_random_documents(db)
    document_ids = [str(doc.id) for doc in documents]

    # Mock questions as QuestionCreate (input to DB), no owner_id yet
    mock_questions = [
        QuestionCreate(
            question=f"Generated question {i}",
            answer=None,
            type=QuestionType.SHORT_ANSWER,
            options=[],
        )
        for i in range(1, 5)
    ]

    payload = {"document_ids": document_ids}

    with patch(
        "app.api.routes.exams.generate_questions_from_documents",
        return_value=mock_questions,
    ):
        response = client.post(
            f"{settings.API_V1_STR}/exams/generate",
            headers=superuser_token_headers,
            json=payload,
        )

    # Response should now contain ExamPublic object with id and owner_id
    assert response.status_code == 200, "Unexpected response status code"
    content = response.json()
    assert len(content) > 0, "Should generate at least one exam"
    # The route attaches owner_id and id

    # assert "id" in content[0], "Generated exam should have an ID"
    # assert "owner_id" in content[0], "Generated exam should have an owner ID"

    assert len(content["questions"]) == len(
        mock_questions
    ), "Number of questions in exam should match generated questions"
