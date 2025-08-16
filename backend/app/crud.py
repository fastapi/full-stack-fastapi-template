from typing import Any
from uuid import UUID

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Document,
    DocumentCreate,
    DocumentPublic,
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
    *, session: Session, document_in: DocumentCreate, owner_id: UUID
) -> DocumentPublic:
    # Validate input and attach owner_id
    db_document = Document.model_validate(document_in, update={"owner_id": owner_id})
    session.add(db_document)
    session.commit()
    session.refresh(db_document)
    # Return Public model for API
    return DocumentPublic.model_validate(db_document)


# --- Question ---
def create_question(
    *, session: Session, question_in: QuestionCreate, owner_id: UUID
) -> QuestionPublic:
    db_question = Question.model_validate(question_in, update={"owner_id": owner_id})
    session.add(db_question)
    session.commit()
    session.refresh(db_question)
    return QuestionPublic.model_validate(db_question)
