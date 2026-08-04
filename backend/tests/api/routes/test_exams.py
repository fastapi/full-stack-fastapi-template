import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import Difficulty, QuestionCreate, QuestionType
from tests.utils.document import create_random_documents
from tests.utils.exam import create_random_exam
from tests.utils.user import get_bootstrap_user


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
            correct_answer="some answer",
            type=QuestionType.multiple_choice,
            options=["option1", "option2", "option3"],
        )
        for i in range(1, 5)
    ]

    payload = {"document_ids": document_ids, "title": "Test Exam"}

    with patch(
        "app.api.routes.exams.generate_questions_from_documents",
        return_value=mock_questions,
    ) as mock_generate:
        response = client.post(
            f"{settings.API_V1_STR}/exams/generate",
            headers=superuser_token_headers,
            json=payload,
        )

        # Verify default values are used
        mock_generate.assert_called_once()
        call_args = mock_generate.call_args
        assert call_args[1]["num_questions"] == 5  # default
        assert call_args[1]["difficulty"] is None  # default
        assert call_args[1]["question_types"] is None  # default

    # Response should now contain ExamPublic object with id and owner_id
    assert response.status_code == 200, "Unexpected response status code"
    content = response.json()
    assert len(content) > 0, "Should generate at least one exam"
    # The route attaches owner_id and id

    # assert "id" in content[0], "Generated exam should have an ID"
    # assert "owner_id" in content[0], "Generated exam should have an owner ID"
    assert content["title"] == "Test Exam", "Exam title should match payload"

    assert len(content["questions"]) == len(
        mock_questions
    ), "Number of questions in exam should match generated questions"


def test_generate_exam_with_customization(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test generating exam with custom num_questions, difficulty, and question_types."""
    documents = create_random_documents(db)
    document_ids = [str(doc.id) for doc in documents]

    mock_questions = [
        QuestionCreate(
            question=f"Generated question {i}",
            correct_answer="some answer",
            type=QuestionType.multiple_choice,
            options=["option1", "option2", "option3"],
        )
        for i in range(1, 8)  # 7 questions
    ]

    payload = {
        "document_ids": document_ids,
        "title": "Customized Test Exam",
        "num_questions": 7,
        "difficulty": "hard",
        "question_types": ["multiple_choice"],
    }

    with patch(
        "app.api.routes.exams.generate_questions_from_documents",
        return_value=mock_questions,
    ) as mock_generate:
        response = client.post(
            f"{settings.API_V1_STR}/exams/generate",
            headers=superuser_token_headers,
            json=payload,
        )

    assert response.status_code == 200
    content = response.json()

    # Verify customization parameters were passed
    mock_generate.assert_called_once()
    call_args = mock_generate.call_args
    assert call_args[1]["num_questions"] == 7
    assert call_args[1]["difficulty"] == Difficulty.hard
    assert call_args[1]["question_types"] == [QuestionType.multiple_choice]

    # Verify exam was created with correct title
    assert content["title"] == "Customized Test Exam", "Exam title should match payload"

    # Verify exam was created with correct number of questions
    assert len(content["questions"]) == 7


def test_generate_exam_with_partial_customization(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test generating exam with only some customization options."""
    documents = create_random_documents(db)
    document_ids = [str(doc.id) for doc in documents]

    mock_questions = [
        QuestionCreate(
            question=f"Generated question {i}",
            correct_answer="some answer",
            type=QuestionType.true_false,
            options=["True", "False"],
        )
        for i in range(1, 4)  # 3 questions
    ]

    payload = {
        "document_ids": document_ids,
        "num_questions": 3,
        "title": "Partial Customization Exam",
        "question_types": ["true_false"],
    }

    with patch(
        "app.api.routes.exams.generate_questions_from_documents",
        return_value=mock_questions,
    ) as mock_generate:
        response = client.post(
            f"{settings.API_V1_STR}/exams/generate",
            headers=superuser_token_headers,
            json=payload,
        )

    assert response.status_code == 200
    content = response.json()

    # Verify partial customization
    mock_generate.assert_called_once()
    call_args = mock_generate.call_args
    assert call_args[1]["num_questions"] == 3
    assert call_args[1]["difficulty"] is None  # not specified
    assert call_args[1]["question_types"] == [QuestionType.true_false]

    # Verify exam was created with correct title
    assert (
        content["title"] == "Partial Customization Exam"
    ), "Exam title should match payload"

    assert len(content["questions"]) == 3


def skip_test_generate_exam_real(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test generating questions from documents using real OpenAI."""

    # Create some test documents
    documents = create_random_documents(db)
    document_ids = [str(doc.id) for doc in documents]

    assert documents[
        0
    ].extracted_text, f"Documents should have extracted text. documents: {documents}"

    payload = {"document_ids": document_ids, "title": "Real API Test Exam"}

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

    assert (
        len(content["questions"]) == 5
    ), f"Number of questions in exam should match generated questions. content: {content}"


def test_read_exam(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    exam = create_random_exam(db, user=get_bootstrap_user(db))
    response = client.get(
        f"{settings.API_V1_STR}/exams/{exam.id}",
        headers=superuser_token_headers,
    )
    content = response.json()
    assert response.status_code == 200, f"content: {content}"

    assert content["title"] == exam.title, f"content: {content}"
    assert content["is_published"] == exam.is_published
    assert content.get("questions")
    assert content["description"] == exam.description
    assert content["duration_minutes"] == exam.duration_minutes
    assert content["id"] == str(exam.id)
    assert content["owner_id"] == str(exam.owner_id)


def test_read_exams(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    owner = get_bootstrap_user(db)
    create_random_exam(db, user=owner)
    create_random_exam(db, user=owner)
    response = client.get(
        f"{settings.API_V1_STR}/exams/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) >= 2


def test_update_exam(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    exam = create_random_exam(db, user=get_bootstrap_user(db))
    data = {"title": "UpdatedKey"}
    response = client.put(
        f"{settings.API_V1_STR}/exams/{exam.id}",
        headers=superuser_token_headers,
        json=data,
    )
    content = response.json()
    assert response.status_code == 200

    assert content["title"] == data["title"]
    assert content["is_published"] == exam.is_published
    assert content.get("questions")
    assert content["description"] == exam.description
    assert content["duration_minutes"] == exam.duration_minutes
    assert content["id"] == str(exam.id)
    assert content["owner_id"] == str(exam.owner_id)


def test_delete_exam(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    exam = create_random_exam(db, user=get_bootstrap_user(db))
    response = client.delete(
        f"{settings.API_V1_STR}/exams/{exam.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Exam deleted successfully"


def test_delete_exam_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/exams/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    content = response.json()
    assert content["detail"] == "Exam not found"


def test_delete_exam_not_enough_permissions(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    exam = create_random_exam(db)
    response = client.delete(
        f"{settings.API_V1_STR}/exams/{exam.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    content = response.json()
    assert content["detail"] == "Not enough permissions"
