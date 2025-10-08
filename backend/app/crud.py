import uuid
from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Answer,
    AnswerUpdate,
    Document,
    DocumentCreate,
    DocumentPublic,
    Exam,
    ExamAttempt,
    ExamAttemptCreate,
    ExamAttemptPublic,
    ExamAttemptUpdate,
    ExamCreate,
    ExamPublic,
    Item,
    ItemCreate,
    Question,
    QuestionCreate,
    QuestionPublic,
    User,
    UserCreate,
    UserUpdate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# --- Document ---
def create_document(
    *,
    session: Session,
    document_in: DocumentCreate,
    owner_id: UUID,
    extracted_text: str | None = None,
) -> DocumentPublic:
    # Validate input and attach owner_id
    update: dict[str, str] = {"owner_id": str(owner_id)}
    if extracted_text is not None:
        update["extracted_text"] = extracted_text
    db_document = Document.model_validate(document_in, update=update)
    session.add(db_document)
    session.commit()
    session.refresh(db_document)
    # Return Public model for API
    return DocumentPublic.model_validate(db_document)


def create_question(
    *, session: Session, question_in: QuestionCreate, exam_id: UUID
) -> QuestionPublic:
    db_question = Question(
        question=question_in.question,
        answer=question_in.answer,
        type=question_in.type,
        options=question_in.options or [],
        exam_id=exam_id,
    )
    session.add(db_question)
    session.commit()
    session.refresh(db_question)
    return QuestionPublic.model_validate(db_question)


def create_db_exam(*, session: Session, exam_in: ExamCreate, owner_id: UUID) -> Exam:
    db_exam = Exam(
        title=exam_in.title,
        description=exam_in.description,
        duration_minutes=exam_in.duration_minutes,
        is_published=exam_in.is_published,
        owner_id=owner_id,
    )
    session.add(db_exam)
    session.commit()
    session.refresh(db_exam)
    return db_exam


def create_exam(
    *, session: Session, db_exam: Exam, questions: list[QuestionCreate]
) -> ExamPublic:
    for question in questions:
        create_question(session=session, question_in=question, exam_id=db_exam.id)

    session.refresh(db_exam, attribute_names=["questions"])
    return ExamPublic.model_validate(db_exam)


def create_exam_attempt(
    *, session: Session, exam_in: ExamAttemptCreate, user_id: UUID
) -> ExamAttemptPublic:
    exam_attempt = ExamAttempt(**exam_in.model_dump(), owner_id=user_id)

    session.add(exam_attempt)
    session.commit()
    return ExamAttemptPublic.model_validate(exam_attempt)


def score_exam_attempt(session: Session, exam_attempt: ExamAttempt) -> float:
    """
    Compute score for an exam attempt and update each answer's is_correct.
    Returns the total score as a float.
    """
    total_questions = len(exam_attempt.answers)
    correct_count = 0

    for answer in exam_attempt.answers:
        question = answer.question  # relationship
        if not question.answer:
            continue  # skip if no answer key

        # Mark whether answer is correct
        is_correct = answer.response.strip().lower() == question.answer.strip().lower()
        answer.is_correct = is_correct
        session.add(answer)

        if is_correct:
            correct_count += 1

    # Compute score as percentage
    score = (correct_count / total_questions) * 100 if total_questions else 0
    exam_attempt.score = score
    session.add(exam_attempt)
    session.commit()
    session.refresh(exam_attempt)

    return score


def update_answers(
    *, session: Session, attempt_id: uuid.UUID, answers_in: list[AnswerUpdate]
) -> list[Answer]:
    updated_answers = []
    for answer_in in answers_in:
        answer = session.get(Answer, answer_in.id)
        if not answer:
            raise ValueError(f"Answer {answer_in.id} not found")
        if answer.attempt_id != attempt_id:
            raise ValueError(
                f"Answer {answer_in.id} does not belong to exam attempt {attempt_id}"
            )
        answer.response = answer_in.response
        session.add(answer)
        updated_answers.append(answer)

    session.commit()
    return updated_answers


def update_exam_attempt(
    *,
    session: Session,
    db_exam_attempt: ExamAttempt,
    exam_attempt_in: ExamAttemptUpdate,
) -> Any:
    """
    Update an exam attempt, including its answers.
    If `is_complete=True`, compute the score.
    """
    # Update attempt-level fields
    if exam_attempt_in.is_complete is not None:
        db_exam_attempt.is_complete = exam_attempt_in.is_complete

    # Delegate answers
    if exam_attempt_in.answers:
        update_answers(
            session=session,
            attempt_id=db_exam_attempt.id,
            answers_in=exam_attempt_in.answers,
        )

    session.add(db_exam_attempt)

    # Score if exam is submitted - do this before commit
    if db_exam_attempt.is_complete:
        score_exam_attempt(session=session, exam_attempt=db_exam_attempt)

    session.commit()
    session.refresh(db_exam_attempt)
    return ExamAttemptPublic.model_validate(db_exam_attempt)
