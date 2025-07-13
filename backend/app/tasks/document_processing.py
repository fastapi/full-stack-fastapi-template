"""
Document Processing Tasks for Celery

This module contains background tasks for processing uploaded documents:
- Text extraction from various file formats
- Intelligent chunking
- Embedding generation
- Database indexing
"""

import json
import logging
import uuid
from datetime import datetime

from celery import current_task
from sqlmodel import Session, select

from app.celery_app import celery_app
from app.core.db import engine
from app.models import (
    Document,
    DocumentChunk,
    DocumentChunkEnhanced,
    DocumentProcessingLog,
    TrainingDocument,
    TrainingDocumentChunkEnhanced,
)
from app.services.document_service import DocumentService
from app.services.enhanced_rag_service import EnhancedRAGService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_document(self, document_id: str, user_id: str, document_type: str = "general"):
    """
    Process an uploaded document: extract text, create chunks, and generate embeddings.
    
    Args:
        document_id: UUID of the document to process
        user_id: UUID of the user who uploaded the document
        document_type: Type of document ("general" or "training")
    """
    try:
        with Session(engine) as session:
            # Get document
            if document_type == "training":
                document = session.get(TrainingDocument, document_id)
            else:
                document = session.get(Document, document_id)

            if not document:
                logger.error(f"Document {document_id} not found")
                return {"status": "error", "message": "Document not found"}

            # Log processing start
            log_entry = DocumentProcessingLog(
                document_id=uuid.UUID(document_id),
                user_id=uuid.UUID(user_id),
                processing_stage="text_extraction",
                status="started"
            )
            session.add(log_entry)
            session.commit()

            # Update document status
            document.processing_status = "processing"
            session.add(document)
            session.commit()

            # Initialize services
            doc_service = DocumentService(session)
            rag_service = EnhancedRAGService(session)

            # Extract text from document
            current_task.update_state(
                state="PROGRESS",
                meta={"stage": "text_extraction", "progress": 10}
            )

            text_content = doc_service.extract_text_from_file(document.file_path)

            if not text_content:
                raise Exception("Failed to extract text from document")

            # Log text extraction completion
            log_entry.status = "completed"
            log_entry.processing_stage = "chunking"
            log_entry.status = "started"
            session.add(log_entry)
            session.commit()

            # Create chunks
            current_task.update_state(
                state="PROGRESS",
                meta={"stage": "chunking", "progress": 30}
            )

            chunks = rag_service.create_intelligent_chunks_sync(
                text_content,
                document_id=document_id,
                user_id=user_id,
                document_type=document_type
            )

            # Log chunking completion
            log_entry.status = "completed"
            log_entry.processing_stage = "embedding"
            log_entry.status = "started"
            log_entry.chunks_created = len(chunks)
            session.add(log_entry)
            session.commit()

            # Generate embeddings
            current_task.update_state(
                state="PROGRESS",
                meta={"stage": "embedding", "progress": 60}
            )

            embedding_results = rag_service.generate_embeddings_batch_sync(
                [chunk.content for chunk in chunks]
            )

            # Store chunks with embeddings
            current_task.update_state(
                state="PROGRESS",
                meta={"stage": "indexing", "progress": 80}
            )

            total_tokens = 0
            for i, (chunk, embedding) in enumerate(zip(chunks, embedding_results, strict=False)):
                chunk.embedding = json.dumps(embedding.tolist())
                session.add(chunk)
                total_tokens += len(chunk.content.split())

            # Update document
            document.processing_status = "completed"
            document.chunk_count = len(chunks)
            session.add(document)

            # Log final completion
            log_entry.status = "completed"
            log_entry.processing_stage = "indexing"
            log_entry.total_tokens = total_tokens
            log_entry.completed_at = datetime.utcnow()
            session.add(log_entry)

            session.commit()

            current_task.update_state(
                state="SUCCESS",
                meta={"stage": "completed", "progress": 100, "chunks_created": len(chunks)}
            )

            return {
                "status": "success",
                "chunks_created": len(chunks),
                "total_tokens": total_tokens,
                "document_id": document_id
            }

    except Exception as exc:
        logger.error(f"Error processing document {document_id}: {exc}")

        # Update document status
        try:
            with Session(engine) as session:
                if document_type == "training":
                    document = session.get(TrainingDocument, document_id)
                else:
                    document = session.get(Document, document_id)

                if document:
                    document.processing_status = "failed"
                    session.add(document)
                    session.commit()

                # Log error
                log_entry = DocumentProcessingLog(
                    document_id=uuid.UUID(document_id),
                    user_id=uuid.UUID(user_id),
                    processing_stage="error",
                    status="failed",
                    error_message=str(exc)
                )
                session.add(log_entry)
                session.commit()

        except Exception as log_exc:
            logger.error(f"Error logging failure: {log_exc}")

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying document processing for {document_id}")
            raise self.retry(exc=exc)

        return {"status": "error", "message": str(exc)}


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def reprocess_failed_document(self, document_id: str, user_id: str, document_type: str = "general"):
    """
    Reprocess a failed document.
    
    Args:
        document_id: UUID of the document to reprocess
        user_id: UUID of the user who uploaded the document
        document_type: Type of document ("general" or "training")
    """
    try:
        with Session(engine) as session:
            # Get document
            if document_type == "training":
                document = session.get(TrainingDocument, document_id)
            else:
                document = session.get(Document, document_id)

            if not document:
                return {"status": "error", "message": "Document not found"}

            # Reset document status
            document.processing_status = "pending"
            session.add(document)
            session.commit()

            # Call main processing task
            return process_document.delay(document_id, user_id, document_type)

    except Exception as exc:
        logger.error(f"Error reprocessing document {document_id}: {exc}")

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)

        return {"status": "error", "message": str(exc)}


@celery_app.task
def batch_process_documents(document_ids: list[str], user_id: str, document_type: str = "general"):
    """
    Process multiple documents in batch.
    
    Args:
        document_ids: List of document UUIDs to process
        user_id: UUID of the user who uploaded the documents
        document_type: Type of documents ("general" or "training")
    """
    results = []

    for doc_id in document_ids:
        try:
            result = process_document.delay(doc_id, user_id, document_type)
            results.append({
                "document_id": doc_id,
                "task_id": result.id,
                "status": "queued"
            })
        except Exception as exc:
            logger.error(f"Error queueing document {doc_id}: {exc}")
            results.append({
                "document_id": doc_id,
                "status": "error",
                "message": str(exc)
            })

    return {
        "status": "success",
        "total_documents": len(document_ids),
        "results": results
    }


@celery_app.task
def cleanup_orphaned_chunks():
    """
    Clean up document chunks that no longer have associated documents.
    """
    try:
        with Session(engine) as session:
            # Find orphaned regular chunks
            orphaned_chunks = session.exec(
                select(DocumentChunk).where(
                    ~DocumentChunk.document_id.in_(
                        select(Document.id)
                    )
                )
            ).all()

            # Find orphaned enhanced chunks
            orphaned_enhanced = session.exec(
                select(DocumentChunkEnhanced).where(
                    ~DocumentChunkEnhanced.document_id.in_(
                        select(Document.id)
                    )
                )
            ).all()

            # Find orphaned training chunks
            orphaned_training = session.exec(
                select(TrainingDocumentChunkEnhanced).where(
                    ~TrainingDocumentChunkEnhanced.training_document_id.in_(
                        select(TrainingDocument.id)
                    )
                )
            ).all()

            # Delete orphaned chunks
            for chunk in orphaned_chunks:
                session.delete(chunk)

            for chunk in orphaned_enhanced:
                session.delete(chunk)

            for chunk in orphaned_training:
                session.delete(chunk)

            session.commit()

            total_cleaned = len(orphaned_chunks) + len(orphaned_enhanced) + len(orphaned_training)

            logger.info(f"Cleaned up {total_cleaned} orphaned chunks")

            return {
                "status": "success",
                "chunks_cleaned": total_cleaned
            }

    except Exception as exc:
        logger.error(f"Error cleaning up orphaned chunks: {exc}")
        return {"status": "error", "message": str(exc)}
