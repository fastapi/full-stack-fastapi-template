from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import QuestionCreate, QuestionPublic, QuestionType
from app.tests.utils.document import create_random_documents


def skip_test_generate_questions(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test generating questions from documents using mocked OpenAI."""
    documents = create_random_documents(db)
    document_ids = [str(doc.id) for doc in documents]

    mock_questions = [
        QuestionPublic(
            id=uuid4(),
            question=f"Generated question {i}",
            answer=None,
            type=QuestionType.SHORT_ANSWER,
            options=[],
            owner_id=uuid4(),  # or use the test user ID
        )
        for i in range(1, 5)
    ]

    payload = {
        "document_ids": document_ids,
    }
    with patch(
        "app.api.routes.questions.generate_questions_from_documents",
        return_value=mock_questions,
    ):
        response = client.post(
            f"{settings.API_V1_STR}/questions/generate",
            headers=superuser_token_headers,
            json=payload,
        )
    assert response.status_code == 200, "Unexpected response status code"
    content = response.json()
    assert isinstance(content, list), "Response should be a list of questions"
    assert len(content) > 0, "Should generate at least one question"
    assert "id" in content[0], "Generated question should have an ID"


from fastapi.testclient import TestClient
from sqlmodel import Session


def test_generate_questions(
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
        "app.api.routes.questions.generate_questions_from_documents",
        return_value=mock_questions,
    ):
        response = client.post(
            f"{settings.API_V1_STR}/questions/generate",
            headers=superuser_token_headers,
            json=payload,
        )

    # Response should now contain QuestionPublic objects with id and owner_id
    assert response.status_code == 200, "Unexpected response status code"
    content = response.json()
    assert isinstance(content, list), "Response should be a list of questions"
    assert len(content) > 0, "Should generate at least one question"
    # The route attaches owner_id and id
    assert "id" in content[0], "Generated question should have an ID"
    assert "owner_id" in content[0], "Generated question should have an owner_id"
