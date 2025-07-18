import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Document, DocumentCreate, DocumentPublic, DocumentsPublic, DocumentUpdate, Message

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_model=DocumentsPublic)
def read_documents(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve documents.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Document)
        count = session.exec(count_statement).one()
        statement = select(Document).offset(skip).limit(limit)
        documents = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Document)
            .where(Document.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Document)
            .where(Document.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        documents = session.exec(statement).all()

    return DocumentsPublic(data=documents, count=count)


@router.get("/{id}", response_model=DocumentPublic)
def read_document(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get document by ID.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if not current_user.is_superuser and (document.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return document


@router.post("/", response_model=DocumentPublic)
def create_document(
    *, session: SessionDep, current_user: CurrentUser, document_in: DocumentCreate
) -> Any:
    """
    Create new document.
    """
    document = Document.model_validate(document_in, update={"owner_id": current_user.id})
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.put("/{id}", response_model=DocumentPublic)
def update_document(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    document_in: DocumentUpdate,
) -> Any:
    """
    Update an document.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if not current_user.is_superuser and (document.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = document_in.model_dump(exclude_unset=True)
    document.sqlmodel_update(update_dict)
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@router.delete("/{id}")
def delete_document(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an document.
    """
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if not current_user.is_superuser and (document.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(document)
    session.commit()
    return Message(message="Document deleted successfully")
