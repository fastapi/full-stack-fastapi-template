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
from app.services.legal import LegalComplianceService
from app.core.auth.roles import role_required, UserRole

router = APIRouter(prefix="/legal", tags=["Legal Compliance"])
legal_service = LegalComplianceService()

# Document Templates Management (Admin/CEO only)
@router.post("/templates", response_model=LegalDocumentTemplate)
@role_required([UserRole.CEO, UserRole.MANAGER])
async def create_legal_template(
    template_data: LegalDocumentTemplateCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new legal document template.
    Only accessible to CEO and Managers.
    """
    try:
        template_data.created_by = current_user.id
        return await legal_service.create_template(template_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating template: {str(e)}"
        )

@router.get("/templates", response_model=List[LegalDocumentTemplate])
@role_required([UserRole.CEO, UserRole.MANAGER, UserRole.AGENT])
async def get_legal_templates(
    document_type: Optional[LegalDocumentType] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get all legal document templates.
    Can be filtered by document type.
    """
    try:
        return await legal_service.get_templates(document_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving templates: {str(e)}"
        )

@router.get("/templates/{template_id}", response_model=LegalDocumentTemplate)
@role_required([UserRole.CEO, UserRole.MANAGER, UserRole.AGENT])
async def get_legal_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get a specific legal document template by ID."""
    try:
        template = await legal_service.get_template_by_id(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        return template
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving template: {str(e)}"
        )

@router.put("/templates/{template_id}", response_model=LegalDocumentTemplate)
@role_required([UserRole.CEO, UserRole.MANAGER])
async def update_legal_template(
    template_id: UUID,
    template_data: LegalDocumentTemplateUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a legal document template."""
    try:
        updated_template = await legal_service.update_template(template_id, template_data)
        if not updated_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        return updated_template
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating template: {str(e)}"
        )

# Document Generation
@router.post("/documents/generate", response_model=GeneratedLegalDocument)
@role_required([UserRole.CEO, UserRole.MANAGER, UserRole.AGENT])
async def generate_legal_document(
    generation_data: GeneratedLegalDocumentCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Generate a legal document from a template.
    Available to CEO, Managers, and Agents.
    """
    try:
        generation_data.generated_by = current_user.id
        return await legal_service.generate_document(generation_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating document: {str(e)}"
        )

@router.get("/documents", response_model=List[GeneratedLegalDocument])
@role_required([UserRole.CEO, UserRole.MANAGER, UserRole.AGENT])
async def get_generated_documents(
    document_type: Optional[LegalDocumentType] = None,
    status_filter: Optional[LegalDocumentStatus] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get generated legal documents.
    Can be filtered by type and status.
    Agents only see their own documents, Managers and CEO see all.
    """
    try:
        user_filter = None
        if current_user.role == UserRole.AGENT:
            user_filter = current_user.id
        
        return await legal_service.get_generated_documents(
            user_id=user_filter,
            document_type=document_type,
            status=status_filter
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving documents: {str(e)}"
        )

@router.get("/documents/{document_id}", response_model=GeneratedLegalDocument)
@role_required([UserRole.CEO, UserRole.MANAGER, UserRole.AGENT])
async def get_generated_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get a specific generated document by ID."""
    try:
        # TODO: Add authorization check to ensure user can access this document
        documents = await legal_service.get_generated_documents()
        document = next((doc for doc in documents if doc.id == document_id), None)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check if user has permission to view this document
        if current_user.role == UserRole.AGENT and document.generated_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return document
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving document: {str(e)}"
        )

@router.put("/documents/{document_id}", response_model=GeneratedLegalDocument)
@role_required([UserRole.CEO, UserRole.MANAGER, UserRole.AGENT])
async def update_generated_document(
    document_id: UUID,
    document_data: GeneratedLegalDocumentUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a generated document status or signatures."""
    try:
        updated_document = await legal_service.update_document_status(document_id, document_data)
        if not updated_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return updated_document
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating document: {str(e)}"
        )

# Compliance Audits (CEO/Manager only)
@router.post("/audits", response_model=ComplianceAudit)
@role_required([UserRole.CEO, UserRole.MANAGER])
async def create_compliance_audit(
    audit_data: ComplianceAuditCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new compliance audit.
    Only accessible to CEO and Managers.
    """
    try:
        audit_data.auditor_id = current_user.id
        return await legal_service.create_compliance_audit(audit_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating audit: {str(e)}"
        )

@router.get("/audits", response_model=List[ComplianceAudit])
@role_required([UserRole.CEO, UserRole.MANAGER])
async def get_compliance_audits(
    current_user: User = Depends(get_current_user)
):
    """Get all compliance audits."""
    try:
        # This would need to be implemented in the service
        return []  # Placeholder
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error retrieving audits: {str(e)}"
        )

# Sample contract templates for quick start
@router.post("/templates/samples", response_model=dict)
@role_required([UserRole.CEO])
async def create_sample_templates(
    current_user: User = Depends(get_current_user)
):
    """
    Create sample legal document templates.
    Only accessible to CEO for initial setup.
    """
    try:
        templates_created = []
        
        # Sale Contract Template
        sale_template = LegalDocumentTemplateCreate(
            template_name="Contrato de Compra-Venta Estándar",
            document_type=LegalDocumentType.SALE_CONTRACT,
            version="1.0",
            content="""
            <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #000000; max-width: 800px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #000000; text-align: center; margin-bottom: 30px;">CONTRATO DE COMPRA-VENTA</h2>
                
                <p><strong>Documento N°:</strong> {{document_number}}</p>
                <p><strong>Fecha:</strong> {{generation_date}}</p>
                
                <h3>PARTES</h3>
                <p><strong>VENDEDOR:</strong> {{seller_name}}, identificado con {{seller_id}}, domiciliado en {{seller_address}}.</p>
                <p><strong>COMPRADOR:</strong> {{buyer_name}}, identificado con {{buyer_id}}, domiciliado en {{buyer_address}}.</p>
                
                <h3>OBJETO DEL CONTRATO</h3>
                <p>El vendedor vende al comprador el inmueble ubicado en {{property_address}}, con las siguientes características:</p>
                <ul>
                    <li>Área: {{property_area}} metros cuadrados</li>
                    <li>Tipo: {{property_type}}</li>
                    <li>Matrícula inmobiliaria: {{property_registry}}</li>
                </ul>
                
                <h3>PRECIO Y FORMA DE PAGO</h3>
                <p>El precio total de la venta es de <strong>{{currency}} {{sale_price}}</strong> ({{sale_price_words}}).</p>
                <p>Forma de pago: {{payment_method}}</p>
                
                <h3>CLÁUSULAS ESPECIALES</h3>
                <p>{{special_clauses}}</p>
                
                <h3>FIRMAS</h3>
                <div style="margin-top: 60px;">
                    <div style="float: left; width: 45%;">
                        <p>_________________________</p>
                        <p><strong>{{seller_name}}</strong><br>VENDEDOR</p>
                    </div>
                    <div style="float: right; width: 45%;">
                        <p>_________________________</p>
                        <p><strong>{{buyer_name}}</strong><br>COMPRADOR</p>
                    </div>
                    <div style="clear: both;"></div>
                </div>
                
                <div style="margin-top: 40px; text-align: center;">
                    <p>_________________________</p>
                    <p><strong>{{name}}</strong><br>INTERMEDIARIO INMOBILIARIO</p>
                </div>
            </div>
            """,
            variables={
                "seller_name": {"type": "string", "required": True, "description": "Nombre del vendedor"},
                "seller_id": {"type": "string", "required": True, "description": "Identificación del vendedor"},
                "seller_address": {"type": "string", "required": True, "description": "Dirección del vendedor"},
                "buyer_name": {"type": "string", "required": True, "description": "Nombre del comprador"},
                "buyer_id": {"type": "string", "required": True, "description": "Identificación del comprador"},
                "buyer_address": {"type": "string", "required": True, "description": "Dirección del comprador"},
                "property_address": {"type": "string", "required": True, "description": "Dirección del inmueble"},
                "property_area": {"type": "number", "required": True, "description": "Área en metros cuadrados"},
                "property_type": {"type": "string", "required": True, "description": "Tipo de inmueble"},
                "property_registry": {"type": "string", "required": True, "description": "Matrícula inmobiliaria"},
                "currency": {"type": "string", "required": True, "description": "Moneda"},
                "sale_price": {"type": "number", "required": True, "description": "Precio de venta"},
                "sale_price_words": {"type": "string", "required": True, "description": "Precio en palabras"},
                "payment_method": {"type": "string", "required": True, "description": "Forma de pago"},
                "special_clauses": {"type": "string", "required": False, "description": "Cláusulas especiales"}
            },
            created_by=current_user.id
        )
        
        sale_template_result = await legal_service.create_template(sale_template)
        templates_created.append(sale_template_result.template_name)
        
        return {
            "message": "Sample templates created successfully",
            "templates": templates_created
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating sample templates: {str(e)}"
        ) 