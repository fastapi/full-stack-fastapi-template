from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session, select

from app.api.deps import (
    CurrentTrainerOrAdmin,
    SessionDep,
    get_user_role,
    UserRole,
)
from app.models import (
    AISoulEntity,
    TrainingDocument,
    TrainingDocumentPublic,
    TrainingMessageCreate,
    TrainingMessagePublic,
    User,
)
from app.services.training_service import TrainingService

router = APIRouter()


@router.post("/{ai_soul_id}/messages", response_model=TrainingMessagePublic)
async def send_training_message(
    *,
    db: SessionDep,
    current_user: CurrentTrainerOrAdmin,
    ai_soul_id: UUID,
    message: TrainingMessageCreate
) -> TrainingMessagePublic:
    """
    Send a training message for an AI soul.
    Only trainers and admins can send training messages.
    """
    training_service = TrainingService(db)

    # Verify AI soul exists
    ai_soul = db.get(AISoulEntity, ai_soul_id)
    if not ai_soul:
        raise HTTPException(status_code=404, detail="AI Soul Entity not found")

    # Only admins can train any soul, trainers can only train their own
    user_role = get_user_role(current_user)
    if user_role == UserRole.TRAINER and ai_soul.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to train this AI soul")

    training_message = await training_service.send_training_message(
        user_id=str(current_user.id),
        ai_soul_id=str(ai_soul_id),
        content=message.content,
        is_from_trainer=message.is_from_trainer
    )

    return TrainingMessagePublic(
        id=training_message.id,
        content=training_message.content,
        is_from_trainer=training_message.is_from_trainer,
        ai_soul_id=training_message.ai_soul_id,
        user_id=training_message.user_id,
        timestamp=training_message.timestamp
    )


@router.get("/{ai_soul_id}/messages", response_model=list[TrainingMessagePublic])
async def get_training_messages(
    *,
    db: SessionDep,
    current_user: CurrentTrainerOrAdmin,
    ai_soul_id: UUID,
    skip: int = 0,
    limit: int = 50
) -> list[TrainingMessagePublic]:
    """
    Get training messages for an AI soul.
    Only trainers and admins can view training messages.
    """
    training_service = TrainingService(db)

    # Verify AI soul exists
    ai_soul = db.get(AISoulEntity, ai_soul_id)
    if not ai_soul:
        raise HTTPException(status_code=404, detail="AI Soul Entity not found")

    # Only admins can view any soul's training, trainers can only view their own
    user_role = get_user_role(current_user)
    if user_role == UserRole.TRAINER and ai_soul.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this AI soul's training")

    messages = training_service.get_training_messages(
        ai_soul_id=str(ai_soul_id),
        user_id=str(current_user.id),
        skip=skip,
        limit=limit
    )

    return [
        TrainingMessagePublic(
            id=message.id,
            content=message.content,
            is_from_trainer=message.is_from_trainer,
            ai_soul_id=message.ai_soul_id,
            user_id=message.user_id,
            timestamp=message.timestamp
        )
        for message in messages
    ]


@router.post("/{ai_soul_id}/documents", response_model=TrainingDocumentPublic)
async def upload_training_document(
    *,
    db: SessionDep,
    current_user: CurrentTrainerOrAdmin,
    ai_soul_id: UUID,
    file: UploadFile = File(...),
    description: str = Form(None)
) -> TrainingDocumentPublic:
    """
    Upload a training document for an AI soul.
    Only trainers and admins can upload training documents.
    """
    training_service = TrainingService(db)

    # Verify AI soul exists
    ai_soul = db.get(AISoulEntity, ai_soul_id)
    if not ai_soul:
        raise HTTPException(status_code=404, detail="AI Soul Entity not found")

    # Only admins can upload to any soul, trainers can only upload to their own
    user_role = get_user_role(current_user)
    if user_role == UserRole.TRAINER and ai_soul.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to upload to this AI soul")

    training_document = await training_service.upload_training_document(
        file=file,
        user_id=str(current_user.id),
        ai_soul_id=str(ai_soul_id),
        description=description
    )

    return TrainingDocumentPublic(
        id=training_document.id,
        filename=training_document.filename,
        original_filename=training_document.original_filename,
        file_size=training_document.file_size,
        content_type=training_document.content_type,
        description=training_document.description,
        ai_soul_id=training_document.ai_soul_id,
        user_id=training_document.user_id,
        upload_timestamp=training_document.upload_timestamp,
        processing_status=training_document.processing_status,
        chunk_count=training_document.chunk_count
    )


@router.get("/{ai_soul_id}/documents", response_model=list[TrainingDocumentPublic])
async def get_training_documents(
    *,
    db: SessionDep,
    current_user: CurrentTrainerOrAdmin,
    ai_soul_id: UUID,
    skip: int = 0,
    limit: int = 20
) -> list[TrainingDocumentPublic]:
    """
    Get training documents for an AI soul.
    Only trainers and admins can view training documents.
    """
    # Verify AI soul exists
    ai_soul = db.get(AISoulEntity, ai_soul_id)
    if not ai_soul:
        raise HTTPException(status_code=404, detail="AI Soul Entity not found")

    # Only admins can view any soul's documents, trainers can only view their own
    user_role = get_user_role(current_user)
    if user_role == UserRole.TRAINER and ai_soul.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this AI soul's documents")

    # Get training documents
    statement = (
        select(TrainingDocument)
        .where(TrainingDocument.ai_soul_id == ai_soul_id)
        .offset(skip)
        .limit(limit)
    )
    documents = db.exec(statement).all()

    return [
        TrainingDocumentPublic(
            id=doc.id,
            filename=doc.filename,
            original_filename=doc.original_filename,
            file_size=doc.file_size,
            content_type=doc.content_type,
            description=doc.description,
            ai_soul_id=doc.ai_soul_id,
            user_id=doc.user_id,
            upload_timestamp=doc.upload_timestamp,
            processing_status=doc.processing_status,
            chunk_count=doc.chunk_count
        )
        for doc in documents
    ]


@router.delete("/{ai_soul_id}/documents/{document_id}")
async def delete_training_document(
    *,
    db: SessionDep,
    current_user: CurrentTrainerOrAdmin,
    ai_soul_id: UUID,
    document_id: UUID
) -> None:
    """
    Delete a training document.
    Only trainers and admins can delete training documents.
    """
    import os

    # Get the document
    document = db.get(TrainingDocument, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Training document not found")

    # Only admins can delete any document, trainers can only delete their own
    user_role = get_user_role(current_user)
    if user_role == UserRole.TRAINER and document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this document")

    # Delete file from disk
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        # Log error but continue with database deletion
        print(f"Error deleting training file {document.file_path}: {e}")

    # Delete from database (will cascade to chunks)
    db.delete(document)
    db.commit()
