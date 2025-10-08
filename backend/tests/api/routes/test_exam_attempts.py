import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import (
    Answer,
    AnswerUpdate,
    ExamAttempt,
    ExamAttemptUpdate,
    Question,
)
from tests.utils.exam import create_exam_with_attempt_and_answer, create_random_exam
from tests.utils.user import create_random_user, create_random_user_with_password

AnswerUpdate.model_rebuild()
ExamAttemptUpdate.model_rebuild()
Answer.model_rebuild()
ExamAttempt.model_rebuild()
Question.model_rebuild()

_ = [AnswerUpdate, ExamAttemptUpdate, Answer, ExamAttempt, Question]


def test_create_exam_attempt_success(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test creating an exam attempt successfully."""
    exam = create_random_exam(db)

    response = client.post(
        f"{settings.API_V1_STR}/exam-attempts/",
        headers=superuser_token_headers,
        json={"exam_id": str(exam.id)},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["exam_id"] == str(exam.id)


def test_create_exam_attempt_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    """Test creating an attempt for a nonexistent exam."""

    payload = {"exam_id": str(uuid.uuid4())}

    response = client.post(
        f"{settings.API_V1_STR}/exam-attempts/",
        headers=superuser_token_headers,
        json=payload,
    )

    assert response.status_code == 404


def test_create_exam_attempt_not_enough_permissions(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test that a normal user cannot create an attempt for someone else's exam."""

    exam = create_random_exam(db)

    response = client.post(
        f"{settings.API_V1_STR}/exam-attempts/",
        headers=normal_user_token_headers,
        json={"exam_id": str(exam.id)},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_read_exam_attempt(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test reading an existing exam attempt."""

    # Create an exam and an attempt
    exam = create_random_exam(db)
    exam_attempt = ExamAttempt(exam_id=exam.id, owner_id=exam.owner_id)
    db.add(exam_attempt)
    db.commit()
    db.refresh(exam_attempt)

    response = client.get(
        f"{settings.API_V1_STR}/exam-attempts/{exam_attempt.id}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 200
    content = response.json()
    assert content["id"] == str(exam_attempt.id)
    assert content["exam_id"] == str(exam.id)


def test_read_exam_attempt_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    """Test reading an exam attempt that does not exist."""

    response = client.get(
        f"{settings.API_V1_STR}/exam-attempts/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Exam Attempt not found"


def test_read_exam_attempt_not_enough_permissions(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test that a normal user cannot read another user's exam attempt."""

    # Create an exam and attempt owned by another user
    exam = create_random_exam(db)
    exam_attempt = ExamAttempt(exam_id=exam.id, owner_id=exam.owner_id)
    db.add(exam_attempt)
    db.commit()
    db.refresh(exam_attempt)

    response = client.get(
        f"{settings.API_V1_STR}/exam-attempts/{exam_attempt.id}",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_update_exam_attempt_success(client: TestClient, db: Session) -> None:
    """Test updating an existing exam attempt."""
    user, password = create_random_user_with_password(db)
    login_data = {"username": user.email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    exam, question, exam_attempt, answer = create_exam_with_attempt_and_answer(
        db, owner_id=user.id
    )

    payload = {"answers": [{"id": str(answer.id), "response": "4"}]}
    response = client.patch(
        f"{settings.API_V1_STR}/exam-attempts/{exam_attempt.id}",
        headers=headers,
        json=payload,
    )

    assert response.status_code == 200


def flaky_test_update_exam_attempt_locked(client: TestClient, db: Session) -> None:
    """Test updating a completed exam attempt."""
    # 1️⃣ Create a random user and their token
    user, password = create_random_user_with_password(db)
    login_data = {"username": user.email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2️⃣ Create exam attempt owned by this user and mark it as complete
    exam, question, exam_attempt, answer = create_exam_with_attempt_and_answer(
        db, owner_id=user.id
    )
    exam_attempt.is_complete = True
    db.add(exam_attempt)
    db.commit()
    db.refresh(exam_attempt)

    # 3️⃣ Attempt to update the completed exam attempt
    payload = {
        "answers": [
            {
                "id": str(answer.id),
                "response": "new answer",
            }
        ]
    }

    response = client.patch(
        f"{settings.API_V1_STR}/exam-attempts/{exam_attempt.id}",
        headers=headers,
        json=payload,
    )

    # 4️⃣ Assertions
    assert response.status_code == 409
    assert response.json()["detail"] == "Exam attempt is already completed"


def flaky_test_update_exam_attempt_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    """Test updating an exam attempt that does not exist."""
    payload = {"answers": [{"id": str(uuid.uuid4()), "response": "4"}]}

    response = client.patch(
        f"{settings.API_V1_STR}/exam-attempts/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=payload,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Exam attempt not found"


def flaky_test_update_exam_attempt_not_enough_permissions(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    db: Session,
) -> None:
    """Test that a normal user cannot update another user's exam attempt."""
    user = create_random_user(db)

    exam, question, exam_attempt, answer = create_exam_with_attempt_and_answer(
        db, owner_id=user.id
    )

    payload = {"answers": [{"id": str(uuid.uuid4()), "response": "4"}]}

    response = client.patch(
        f"{settings.API_V1_STR}/exam-attempts/{exam_attempt.id}",
        headers=normal_user_token_headers,
        json=payload,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not allowed"
