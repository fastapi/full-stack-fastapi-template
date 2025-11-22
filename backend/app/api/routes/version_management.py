import uuid
from typing import Any
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import DocumentVersion, DocumentVersionRead

router = APIRouter()

@router.get("/{id}/compare/{version1_id}/{version2_id}")
def compare_versions(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    version1_id: uuid.UUID,
    version2_id: uuid.UUID
) -> Any:
    """
    Compare two document versions (returns metadata for now, diff visualization would be frontend).
    """
    version1 = session.get(DocumentVersion, version1_id)
    version2 = session.get(DocumentVersion, version2_id)
    
    if not version1 or not version2:
        raise HTTPException(status_code=404, detail="Version not found")
        
    if version1.document_id != id or version2.document_id != id:
        raise HTTPException(status_code=400, detail="Versions do not belong to this document")
        
    # Get file sizes for comparison
    from app.services.file_storage import storage_service
    
    path1 = storage_service.get_file_path(version1.file_path)
    path2 = storage_service.get_file_path(version2.file_path)
    
    size1 = path1.stat().st_size if path1.exists() else 0
    size2 = path2.stat().st_size if path2.exists() else 0
    
    return {
        "version1": {
            "id": version1.id,
            "version_number": version1.version_number,
            "created_at": version1.created_at,
            "created_by_id": version1.created_by_id,
            "file_size": size1
        },
        "version2": {
            "id": version2.id,
            "version_number": version2.version_number,
            "created_at": version2.created_at,
            "created_by_id": version2.created_by_id,
            "file_size": size2
        },
        "size_difference": size2 - size1
    }

@router.get("/{id}/metadata")
def get_document_metadata(
    *, session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get file metadata for the latest document version.
    """
    from app.models import Document
    from app.services.file_storage import storage_service
    
    document = session.get(Document, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Get latest version
    latest_version = session.exec(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == id)
        .order_by(DocumentVersion.version_number.desc())
    ).first()
    
    if not latest_version:
        raise HTTPException(status_code=404, detail="No versions found")
        
    file_path = storage_service.get_file_path(latest_version.file_path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    stat = file_path.stat()
    
    return {
        "document_id": document.id,
        "title": document.title,
        "current_version": latest_version.version_number,
        "file_name": file_path.name,
        "file_size": stat.st_size,
        "file_extension": file_path.suffix,
        "last_modified": stat.st_mtime,
        "created_at": document.created_at,
        "status": document.status
    }
