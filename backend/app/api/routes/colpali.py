"""
ColPali API routes for document embedding and search functionality.
"""
from typing import Any

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.api.deps import CurrentUser
from app.models import (
    ColPaliSearchRequest,
    ColPaliSearchResponse,
    ColPaliSearchResult,
    ColPaliUploadRequest,
    ColPaliUploadResponse,
    Message,
)
from app.services.colpali import colpali_service

router = APIRouter(prefix="/colpali", tags=["colpali"])


@router.post("/search", response_model=ColPaliSearchResponse)
def search_documents(
    current_user: CurrentUser,
    search_request: ColPaliSearchRequest,
) -> Any:
    """
    Search for documents using ColPali semantic search.
    
    This endpoint allows users to search through embedded documents using natural language queries.
    The search uses ColPali's multimodal embedding approach with reranking for improved results.
    """
    try:
        # Perform search using ColPali service
        results = colpali_service.search(
            query=search_request.query,
            collection_name=search_request.collection_name,
            search_limit=search_request.search_limit,
            prefetch_limit=search_request.prefetch_limit,
        )
        
        # Format results
        search_results = [
            ColPaliSearchResult(
                id=result["id"],
                score=result["score"],
                payload=result["payload"]
            )
            for result in results
        ]
        
        return ColPaliSearchResponse(
            results=search_results,
            query=search_request.query,
            collection_name=search_request.collection_name,
            total_results=len(search_results)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/upload", response_model=ColPaliUploadResponse)
def upload_dataset(
    current_user: CurrentUser,
    upload_request: ColPaliUploadRequest,
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Upload a dataset to Qdrant collection for ColPali search.
    
    This endpoint processes and embeds documents from a specified dataset,
    then uploads them to a Qdrant collection for later search operations.
    The upload process runs in the background to avoid request timeouts.
    """
    try:
        # Start upload process in background
        def upload_task():
            return colpali_service.upload_dataset(
                dataset_name=upload_request.dataset_name,
                collection_name=upload_request.collection_name,
                batch_size=upload_request.batch_size,
            )
        
        # For now, we'll run synchronously but this could be made async
        result = upload_task()
        
        return ColPaliUploadResponse(
            message=f"Upload completed. {result['total_uploaded']} out of {result['total_items']} items uploaded successfully.",
            collection_name=upload_request.collection_name,
            total_uploaded=result["total_uploaded"],
            total_items=result["total_items"],
            success=result["success"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/collections", response_model=list[str])
def list_collections(current_user: CurrentUser) -> Any:
    """
    List all available Qdrant collections.
    
    Returns a list of collection names that are available for search operations.
    """
    try:
        collections = colpali_service.client.get_collections().collections
        return [collection.name for collection in collections]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list collections: {str(e)}"
        )


@router.get("/collections/{collection_name}/info")
def get_collection_info(
    current_user: CurrentUser,
    collection_name: str,
) -> Any:
    """
    Get information about a specific collection.
    
    Returns metadata and statistics about the specified collection.
    """
    try:
        collection_info = colpali_service.client.get_collection(collection_name)
        return {
            "name": collection_name,
            "vectors_count": collection_info.vectors_count,
            "indexed_vectors_count": collection_info.indexed_vectors_count,
            "points_count": collection_info.points_count,
            "segments_count": collection_info.segments_count,
            "config": {
                "params": collection_info.config.params.dict() if collection_info.config.params else None,
                "hnsw_config": collection_info.config.hnsw_config.dict() if collection_info.config.hnsw_config else None,
                "optimizer_config": collection_info.config.optimizer_config.dict() if collection_info.config.optimizer_config else None,
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get collection info: {str(e)}"
        )


@router.delete("/collections/{collection_name}", response_model=Message)
def delete_collection(
    current_user: CurrentUser,
    collection_name: str,
) -> Any:
    """
    Delete a collection and all its data.
    
    WARNING: This operation is irreversible and will delete all embedded documents
    in the specified collection.
    """
    try:
        # Check if user is superuser for destructive operations
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=403,
                detail="Only superusers can delete collections"
            )
        
        colpali_service.client.delete_collection(collection_name)
        return Message(message=f"Collection '{collection_name}' deleted successfully")
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete collection: {str(e)}"
        )


@router.post("/collections/{collection_name}/create", response_model=Message)
def create_collection(
    current_user: CurrentUser,
    collection_name: str,
) -> Any:
    """
    Create a new empty collection for ColPali embeddings.
    
    Creates a new Qdrant collection with the appropriate vector configuration
    for ColPali embeddings (original, mean_pooling_rows, mean_pooling_columns).
    """
    try:
        created = colpali_service.create_collection_if_not_exists(collection_name)
        
        if created:
            return Message(message=f"Collection '{collection_name}' created successfully")
        else:
            return Message(message=f"Collection '{collection_name}' already exists")
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create collection: {str(e)}"
        )


@router.get("/health")
def health_check() -> Any:
    """
    Health check endpoint for ColPali service.
    
    Verifies that the ColPali model, Qdrant client, and other dependencies
    are properly initialized and accessible.
    """
    try:
        # Check Qdrant connection
        collections = colpali_service.client.get_collections()
        
        # Check model initialization
        model_ready = colpali_service.model is not None and colpali_service.processor is not None
        
        return {
            "status": "healthy",
            "qdrant_connected": True,
            "collections_count": len(collections.collections),
            "model_ready": model_ready,
            "device": str(colpali_service.model.device) if colpali_service.model else "unknown"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "qdrant_connected": False,
                "model_ready": False
            }
        )
