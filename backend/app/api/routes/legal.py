from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status

from app.api.deps import get_current_user
from app.models import (
    User, LegalDocumentTemplate, LegalDocumentTemplateCreate, LegalDocumentTemplateUpdate,
    GeneratedLegalDocument, GeneratedLegalDocumentCreate, GeneratedLegalDocumentUpdate,
    ComplianceAudit, ComplianceAuditCreate,
    DataProtectionConsent, DataProtectionConsentCreate,
    LegalDocumentType, LegalDocumentStatus
)

router = APIRouter(prefix="/legal", tags=["Legal Compliance"])

# Document Templates Management (temporalmente sin restricciones)
@router.post("/templates", response_model=dict)
async def create_legal_template(
    template_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new legal document template.
    Temporarily simplified for development.
    """
    try:
        return {
            "message": "Template creation endpoint - temporarily simplified",
            "user": current_user.email,
            "data": template_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating template: {str(e)}"
        )

@router.get("/templates", response_model=List[dict])
async def get_legal_templates(
    document_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get all legal document templates.
    Temporarily simplified for development.
    """
    try:
        return [
            {
                "id": "template-1",
                "name": "Sample Contract Template",
                "type": document_type or "sample",
                "user": current_user.email
            }
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving templates: {str(e)}"
        )

@router.get("/templates/{template_id}", response_model=dict)
async def get_legal_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get a specific legal document template by ID."""
    try:
        return {
            "id": str(template_id),
            "name": "Sample Template",
            "user": current_user.email
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving template: {str(e)}"
        )

@router.get("/health", response_model=dict)
async def legal_health_check():
    """Legal module health check."""
    return {
        "status": "healthy",
        "module": "legal",
        "message": "Legal compliance module is operational"
    }