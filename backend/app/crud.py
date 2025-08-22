from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Document,
    DocumentCreate,
    DocumentPublic,
    Exam,
    ExamCreate,
    ExamPublic,
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
