import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_user, get_db
from app.models import Document, DocumentPublic, DocumentsPublic, User
from app.services.enhanced_rag_service import EnhancedRAGService

router = APIRouter()


@router.post("/upload/", response_model=DocumentPublic)
async def upload_document(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    file: UploadFile = File(...),
    description: str | None = Form(None),
) -> DocumentPublic:
    """
    Upload a PDF document for processing.
    """
    import os

    from app.core.config import settings

    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Read file content and validate
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large")

    # Create upload directory if it doesn't exist
    upload_dir = getattr(settings, 'UPLOAD_DIR', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    import hashlib
    file_hash = hashlib.md5(content).hexdigest()
    ext = os.path.splitext(file.filename or "document.pdf")[1]
    filename = f"{file_hash}{ext}"
    file_path = os.path.join(upload_dir, filename)

    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(content)

    # Create document record
    document = Document(
        filename=filename,
        original_filename=file.filename or "document.pdf",
        file_size=len(content),
        content_type=file.content_type,
        description=description,
        file_path=file_path,
        user_id=current_user.id,
        processing_status="pending",
        chunk_count=0,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Process document with Enhanced RAG service
    try:
        rag_service = EnhancedRAGService(db)
        await rag_service.process_document(
            document=document,
            user_id=str(current_user.id)
        )

        # Update document status
        document.processing_status = "completed"
        db.commit()

    except Exception as e:
        document.processing_status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

    return DocumentPublic.from_orm(document)


@router.get("/", response_model=DocumentsPublic)
def get_documents(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> DocumentsPublic:
    """
    Retrieve all documents for the current user.
    """
    # Get documents directly from database
    query = select(Document).where(Document.user_id == current_user.id)
    total = len(db.exec(query).all())

    documents = db.exec(
        query.offset(skip).limit(limit)
    ).all()

    return DocumentsPublic(
        data=[DocumentPublic.from_orm(doc) for doc in documents],
        count=total,
    )


@router.delete("/{document_id}")
async def delete_document(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    document_id: uuid.UUID,
) -> dict:
    """
    Delete a document and its associated file.
    """
    # Get the document
    document = db.exec(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from Qdrant
    try:
        rag_service = EnhancedRAGService(db)
        await rag_service.delete_document_from_index(
            document_id=str(document_id),
            user_id=str(current_user.id)
        )
    except Exception as e:
        # Log error but don't fail the deletion
        print(f"Warning: Failed to delete from Qdrant: {e}")

    # Delete file from disk
    import os
    if document.file_path and os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except Exception as e:
            print(f"Warning: Failed to delete file: {e}")

    # Delete from database
    db.delete(document)
    db.commit()

    return {"status": "success", "message": "Document deleted"}


@router.get("/{document_id}", response_model=DocumentPublic)
def get_document(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    document_id: uuid.UUID,
) -> DocumentPublic:
    """
    Get a specific document by ID.
    """
    document = db.exec(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentPublic.from_orm(document)


@router.post("/search")
async def search_documents(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    query: str = Form(...),
    limit: int = Form(5)
) -> Any:
    """
    Search through uploaded documents using Enhanced RAG.
    """
    try:
        rag_service = EnhancedRAGService(db)
        search_response = await rag_service.hybrid_search(
            query=query,
            user_id=str(current_user.id),
            limit=limit
        )

        return {
            "query": query,
            "results": search_response.get("results", []),
            "total_found": search_response.get("total_found", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")


@router.get("/stats/summary")
def get_document_stats(*, session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get document statistics for the current user.
    """
    try:
        # Get document count by status
        statement = select(Document).where(Document.user_id == current_user.id)
        documents = session.exec(statement).all()

        stats = {
            "total_documents": len(documents),
            "completed": len([d for d in documents if d.processing_status == "completed"]),
            "processing": len([d for d in documents if d.processing_status == "processing"]),
            "pending": len([d for d in documents if d.processing_status == "pending"]),
            "failed": len([d for d in documents if d.processing_status == "failed"]),
            "total_chunks": sum(d.chunk_count for d in documents),
            "total_size_mb": round(sum(d.file_size for d in documents) / (1024 * 1024), 2)
        }

        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting document stats: {str(e)}")
