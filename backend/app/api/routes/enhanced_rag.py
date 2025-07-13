"""
Enhanced RAG API Routes

Provides REST endpoints for the enhanced RAG system including:
- Document search with hybrid retrieval
- Document processing and indexing
- Search analytics and monitoring
- Configuration management
- Health checks and system status
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.api.deps import get_current_user, get_db
from app.models import Document, User
from app.services.enhanced_rag_service import EnhancedRAGService

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for request/response
class SearchRequest(BaseModel):
    """Search request model."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    ai_soul_id: str | None = Field(None, description="AI Soul ID for filtering")
    filters: dict[str, Any] | None = Field(None, description="Additional search filters")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results")


class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    results: list[dict[str, Any]]
    total_found: int
    response_time_ms: int
    search_algorithm: str
    similarity_threshold: float
    reranking_enabled: bool


class ProcessDocumentRequest(BaseModel):
    """Document processing request model."""
    document_id: str = Field(..., description="Document ID to process")
    chunking_strategy: str | None = Field("semantic", description="Chunking strategy")
    chunk_size: int | None = Field(500, ge=100, le=2000, description="Chunk size")
    chunk_overlap: int | None = Field(50, ge=0, le=500, description="Chunk overlap")
    embedding_model: str | None = Field("text-embedding-3-small", description="Embedding model")


class ProcessDocumentResponse(BaseModel):
    """Document processing response model."""
    status: str
    chunks_created: int
    processing_time_ms: int
    embedding_model: str
    chunking_strategy: str


class ClickTrackingRequest(BaseModel):
    """Click tracking request model."""
    search_query_id: str
    chunk_id: str
    result_position: int
    similarity_score: float
    rerank_score: float | None = None


class ConfigurationRequest(BaseModel):
    """RAG configuration request model."""
    ai_soul_id: str | None = None
    chunking_strategy: str = Field("semantic", pattern="^(semantic|sentence|paragraph|simple)$")
    chunk_size: int = Field(500, ge=100, le=2000)
    chunk_overlap: int = Field(50, ge=0, le=500)
    embedding_model: str = Field("text-embedding-3-small")
    search_algorithm: str = Field("hybrid", pattern="^(vector|hybrid|keyword)$")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)
    max_results: int = Field(10, ge=1, le=100)
    enable_reranking: bool = True


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search documents using enhanced RAG with hybrid retrieval.
    
    Features:
    - Semantic vector search
    - Keyword matching
    - Result reranking
    - Caching for performance
    - Analytics tracking
    """
    try:
        rag_service = EnhancedRAGService(db)

        # Perform hybrid search with fallback
        results = await rag_service.simple_hybrid_search(
            query=request.query,
            user_id=str(current_user.id),
            ai_soul_id=request.ai_soul_id,
            filters=request.filters,
            limit=request.limit
        )

        return SearchResponse(**results)

    except Exception as e:
        logger.error(f"Search error for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/documents/process", response_model=ProcessDocumentResponse)
async def process_document(
    request: ProcessDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a document with enhanced chunking and indexing.
    
    Steps:
    1. Extract text from document
    2. Apply intelligent chunking
    3. Generate embeddings
    4. Store in vector database
    5. Update analytics
    """
    try:
        # Get document
        document = db.get(Document, uuid.UUID(request.document_id))
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Check ownership
        if document.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Create RAG service and process document
        rag_service = EnhancedRAGService(db)

        # Create custom config if provided
        config = None
        if any([
            request.chunking_strategy != "semantic",
            request.chunk_size != 500,
            request.chunk_overlap != 50,
            request.embedding_model != "text-embedding-3-small"
        ]):
            from app.models import RAGConfiguration
            config = RAGConfiguration(
                user_id=current_user.id,
                chunking_strategy=request.chunking_strategy,
                chunk_size=request.chunk_size,
                chunk_overlap=request.chunk_overlap,
                embedding_model=request.embedding_model,
                search_algorithm="hybrid",
                similarity_threshold=0.7,
                max_results=10,
                enable_reranking=True
            )

        result = await rag_service.process_document(
            document=document,
            user_id=str(current_user.id),
            config=config
        )

        return ProcessDocumentResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document processing error for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )


@router.post("/documents/{document_id}/reindex")
async def reindex_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reindex an existing document with current configuration.
    
    This will:
    1. Delete existing chunks from vector database
    2. Reprocess the document with current settings
    3. Create new embeddings and chunks
    """
    try:
        # Get document
        document = db.get(Document, uuid.UUID(document_id))
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Check ownership
        if document.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        rag_service = EnhancedRAGService(db)

        # Delete existing index
        await rag_service.delete_document_from_index(
            document_id=document_id,
            user_id=str(current_user.id)
        )

        # Reprocess document
        result = await rag_service.process_document(
            document=document,
            user_id=str(current_user.id)
        )

        return {
            "message": "Document reindexed successfully",
            "document_id": document_id,
            **result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document reindexing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reindexing failed: {str(e)}"
        )


@router.delete("/documents/{document_id}/index")
async def delete_document_index(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete document chunks from the vector index.
    
    This removes all chunks and embeddings for the document
    but keeps the document record intact.
    """
    try:
        rag_service = EnhancedRAGService(db)

        success = await rag_service.delete_document_from_index(
            document_id=document_id,
            user_id=str(current_user.id)
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document index"
            )

        return {
            "message": "Document index deleted successfully",
            "document_id": document_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document index deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Index deletion failed: {str(e)}"
        )


@router.post("/analytics/click")
async def track_result_click(
    request: ClickTrackingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track when a user clicks on a search result.
    
    This helps improve search relevance through user feedback
    and provides analytics on result effectiveness.
    """
    try:
        rag_service = EnhancedRAGService(db)

        await rag_service.track_result_click(
            search_query_id=request.search_query_id,
            chunk_id=request.chunk_id,
            user_id=str(current_user.id),
            result_position=request.result_position,
            similarity_score=request.similarity_score,
            rerank_score=request.rerank_score
        )

        return {"message": "Click tracked successfully"}

    except Exception as e:
        logger.error(f"Click tracking error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Click tracking failed: {str(e)}"
        )


@router.get("/analytics/search")
async def get_search_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get search analytics for the current user.
    
    Returns:
    - Total searches performed
    - Average response time
    - Click-through rate
    - Top search queries
    """
    try:
        rag_service = EnhancedRAGService(db)

        analytics = await rag_service.get_search_analytics(
            user_id=str(current_user.id),
            days=days
        )

        return analytics

    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics retrieval failed: {str(e)}"
        )


@router.get("/configuration")
async def get_rag_configuration(
    ai_soul_id: str | None = Query(None, description="AI Soul ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get RAG configuration for user or specific AI Soul."""
    try:
        from sqlmodel import select

        from app.models import RAGConfiguration

        query = select(RAGConfiguration).where(
            RAGConfiguration.user_id == current_user.id
        )

        if ai_soul_id:
            query = query.where(RAGConfiguration.ai_soul_id == uuid.UUID(ai_soul_id))
        else:
            query = query.where(RAGConfiguration.ai_soul_id.is_(None))

        config = db.exec(query).first()

        if not config:
            # Return default configuration
            return {
                "chunking_strategy": "semantic",
                "chunk_size": 500,
                "chunk_overlap": 50,
                "embedding_model": "text-embedding-3-small",
                "search_algorithm": "hybrid",
                "similarity_threshold": 0.7,
                "max_results": 10,
                "enable_reranking": True,
                "is_default": True
            }

        return {
            "id": str(config.id),
            "ai_soul_id": str(config.ai_soul_id) if config.ai_soul_id else None,
            "chunking_strategy": config.chunking_strategy,
            "chunk_size": config.chunk_size,
            "chunk_overlap": config.chunk_overlap,
            "embedding_model": config.embedding_model,
            "search_algorithm": config.search_algorithm,
            "similarity_threshold": config.similarity_threshold,
            "max_results": config.max_results,
            "enable_reranking": config.enable_reranking,
            "advanced_settings": config.advanced_settings,
            "created_at": config.created_at,
            "updated_at": config.updated_at,
            "is_default": False
        }

    except Exception as e:
        logger.error(f"Configuration retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration retrieval failed: {str(e)}"
        )


@router.post("/configuration")
async def update_rag_configuration(
    request: ConfigurationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update RAG configuration for user or specific AI Soul."""
    try:
        from datetime import datetime

        from sqlmodel import select

        from app.models import RAGConfiguration

        # Check if configuration exists
        query = select(RAGConfiguration).where(
            RAGConfiguration.user_id == current_user.id
        )

        if request.ai_soul_id:
            query = query.where(RAGConfiguration.ai_soul_id == uuid.UUID(request.ai_soul_id))
        else:
            query = query.where(RAGConfiguration.ai_soul_id.is_(None))

        config = db.exec(query).first()

        if config:
            # Update existing configuration
            config.chunking_strategy = request.chunking_strategy
            config.chunk_size = request.chunk_size
            config.chunk_overlap = request.chunk_overlap
            config.embedding_model = request.embedding_model
            config.search_algorithm = request.search_algorithm
            config.similarity_threshold = request.similarity_threshold
            config.max_results = request.max_results
            config.enable_reranking = request.enable_reranking
            config.updated_at = datetime.utcnow()
        else:
            # Create new configuration
            config = RAGConfiguration(
                user_id=current_user.id,
                ai_soul_id=uuid.UUID(request.ai_soul_id) if request.ai_soul_id else None,
                chunking_strategy=request.chunking_strategy,
                chunk_size=request.chunk_size,
                chunk_overlap=request.chunk_overlap,
                embedding_model=request.embedding_model,
                search_algorithm=request.search_algorithm,
                similarity_threshold=request.similarity_threshold,
                max_results=request.max_results,
                enable_reranking=request.enable_reranking
            )
            db.add(config)

        db.commit()
        db.refresh(config)

        return {
            "message": "Configuration updated successfully",
            "id": str(config.id),
            "ai_soul_id": str(config.ai_soul_id) if config.ai_soul_id else None
        }

    except Exception as e:
        logger.error(f"Configuration update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration update failed: {str(e)}"
        )


@router.get("/health")
async def health_check(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Perform health check on RAG system components.
    
    Checks:
    - Qdrant vector database connectivity
    - Redis cache availability
    - OpenAI API connectivity
    - Database connectivity
    """
    try:
        rag_service = EnhancedRAGService(db)
        health = await rag_service.health_check()

        return health

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/collections/info")
async def get_collection_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get information about Qdrant collections.
    
    Returns collection statistics and status for monitoring.
    """
    try:
        rag_service = EnhancedRAGService(db)
        info = await rag_service.get_collection_info()

        return info

    except Exception as e:
        logger.error(f"Collection info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Collection info retrieval failed: {str(e)}"
        )


@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on query prefix.
    
    Returns popular queries that start with the given prefix
    to help users with query completion.
    """
    try:
        from sqlmodel import func, select

        from app.models import SearchQuery

        # Get popular queries that start with the prefix
        suggestions = db.exec(
            select(SearchQuery.query_text, func.count(SearchQuery.id).label('count'))
            .where(
                SearchQuery.user_id == current_user.id,
                SearchQuery.query_text.ilike(f"{query}%")
            )
            .group_by(SearchQuery.query_text)
            .order_by(func.count(SearchQuery.id).desc())
            .limit(limit)
        ).all()

        return {
            "query": query,
            "suggestions": [{"text": s.query_text, "count": s.count} for s in suggestions]
        }

    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Suggestions retrieval failed: {str(e)}"
        )


@router.post("/bulk-process")
async def bulk_process_documents(
    document_ids: list[str],
    chunking_strategy: str = "semantic",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process multiple documents in bulk.
    
    Useful for reprocessing documents after configuration changes
    or initial setup of large document collections.
    """
    try:
        if len(document_ids) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 documents can be processed at once"
            )

        rag_service = EnhancedRAGService(db)
        results = []

        for doc_id in document_ids:
            try:
                document = db.get(Document, uuid.UUID(doc_id))
                if not document or document.user_id != current_user.id:
                    results.append({
                        "document_id": doc_id,
                        "status": "error",
                        "error": "Document not found or access denied"
                    })
                    continue

                result = await rag_service.process_document(
                    document=document,
                    user_id=str(current_user.id)
                )

                results.append({
                    "document_id": doc_id,
                    **result
                })

            except Exception as e:
                results.append({
                    "document_id": doc_id,
                    "status": "error",
                    "error": str(e)
                })

        return {
            "message": "Bulk processing completed",
            "total_documents": len(document_ids),
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk processing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk processing failed: {str(e)}"
        )
