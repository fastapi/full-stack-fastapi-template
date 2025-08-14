from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.tests.utils.document import create_random_documents


def test_generate_questions(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test generating questions from documents using mocked OpenAI."""
    documents = create_random_documents(db)
    document_ids = [doc.id for doc in documents]
    payload = {
        "document_ids": document_ids,
    }
    with patch(
        "app.api.routes.questions.generate_questions_from_documents",
        return_value=[
            "Generated question 1",
            "Generated question 2",
            "Generated question 3",
            "Generated question 4",
        ],
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
