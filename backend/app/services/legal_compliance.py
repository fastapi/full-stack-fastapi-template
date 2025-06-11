from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import re
from jinja2 import Template
import base64

from app.core.nhost_client import nhost_client
from app.models import (
    LegalDocumentTemplate, LegalDocumentTemplateCreate, LegalDocumentTemplateUpdate,
    GeneratedLegalDocument, GeneratedLegalDocumentCreate, GeneratedLegalDocumentUpdate,
    ComplianceAudit, ComplianceAuditCreate,
    DataProtectionConsent, DataProtectionConsentCreate,
    LegalDocumentType, LegalDocumentStatus
)

class LegalComplianceService:
    """Service for handling legal compliance, document templates, and document generation"""

    def __init__(self):
        self.client = nhost_client

    # Corporate Branding
    COMPANY_LOGO_BASE64 = """
    data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==
    """  # Placeholder - replace with actual logo
    
    COMPANY_INFO = {
        "name": "GENIUS INDUSTRIES",
        "address": "Dirección Corporativa",
        "phone": "+1 (555) 123-4567",
        "email": "info@genius-industries.com",
        "website": "www.genius-industries.com",
        "tax_id": "12345678-9"
    }

    def get_document_header(self) -> str:
        """Generate corporate header with logo for all documents"""
        return f"""
        <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #000000; padding-bottom: 20px;">
            <img src="{self.COMPANY_LOGO_BASE64}" alt="GENIUS INDUSTRIES Logo" style="max-height: 80px; margin-bottom: 10px;">
            <h1 style="color: #000000; font-family: 'Arial', sans-serif; margin: 0; font-size: 24px; font-weight: bold;">
                {self.COMPANY_INFO['name']}
            </h1>
            <p style="color: #666666; margin: 5px 0; font-size: 12px;">
                {self.COMPANY_INFO['address']} | Tel: {self.COMPANY_INFO['phone']} | Email: {self.COMPANY_INFO['email']}
            </p>
        </div>
        """

    def get_document_footer(self) -> str:
        """Generate corporate footer for all documents"""
        return f"""
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #E5E5E5; text-align: center; font-size: 10px; color: #999999;">
            <p>{self.COMPANY_INFO['name']} - {self.COMPANY_INFO['website']}</p>
            <p>Este documento ha sido generado electrónicamente y es válido sin firma física</p>
            <p>Documento generado el: {{generation_date}}</p>
        </div>
        """

    # Template Management
    async def create_template(self, template_data: LegalDocumentTemplateCreate) -> LegalDocumentTemplate:
        """Create a new legal document template"""
        mutation = """
        mutation CreateLegalDocumentTemplate($template: legal_document_templates_insert_input!) {
            insert_legal_document_templates_one(object: $template) {
                id
                template_name
                document_type
                version
                content
                variables
                is_active
                created_by
                created_at
                updated_at
            }
        }
        """

        # Add corporate branding to template content
        full_content = (
            self.get_document_header() +
            template_data.content +
            self.get_document_footer()
        )

        variables = {
            "template": {
                **template_data.dict(),
                "content": full_content,
                "id": str(uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        }

        result = await self.client.execute_mutation(mutation, variables)
        return LegalDocumentTemplate(**result["data"]["insert_legal_document_templates_one"])

    async def get_templates(self, document_type: Optional[LegalDocumentType] = None) -> List[LegalDocumentTemplate]:
        """Get all legal document templates, optionally filtered by type"""
        query = """
        query GetLegalDocumentTemplates($where: legal_document_templates_bool_exp) {
            legal_document_templates(where: $where, order_by: {created_at: desc}) {
                id
                template_name
                document_type
                version
                content
                variables
                is_active
                created_by
                created_at
                updated_at
            }
        }
        """

        where_clause = {"is_active": {"_eq": True}}
        if document_type:
            where_clause["document_type"] = {"_eq": document_type}

        variables = {"where": where_clause}
        result = await self.client.execute_query(query, variables)
        return [LegalDocumentTemplate(**template) for template in result["data"]["legal_document_templates"]]

    async def update_template(self, template_id: UUID, template_data: LegalDocumentTemplateUpdate) -> Optional[LegalDocumentTemplate]:
        """Update a legal document template"""
        mutation = """
        mutation UpdateLegalDocumentTemplate($id: uuid!, $template: legal_document_templates_set_input!) {
            update_legal_document_templates_by_pk(pk_columns: {id: $id}, _set: $template) {
                id
                template_name
                document_type
                version
                content
                variables
                is_active
                created_by
                created_at
                updated_at
            }
        }
        """

        update_data = {k: v for k, v in template_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow().isoformat()

        variables = {
            "id": str(template_id),
            "template": update_data
        }

        result = await self.client.execute_mutation(mutation, variables)
        template_data = result["data"]["update_legal_document_templates_by_pk"]
        return LegalDocumentTemplate(**template_data) if template_data else None

    # Document Generation
    async def generate_document(self, generation_data: GeneratedLegalDocumentCreate) -> GeneratedLegalDocument:
        """Generate a legal document from a template"""
        # Get template
        template = await self.get_template_by_id(generation_data.template_id)
        if not template:
            raise ValueError("Template not found")

        # Generate document content
        template_obj = Template(template.content)
        
        # Add corporate info and generation date to variables
        variables_with_corporate = {
            **generation_data.variables_used,
            **self.COMPANY_INFO,
            "generation_date": datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
        }
        
        generated_content = template_obj.render(**variables_with_corporate)

        # Generate unique document number
        document_number = await self.generate_document_number(template.document_type)

        mutation = """
        mutation CreateGeneratedLegalDocument($document: generated_legal_documents_insert_input!) {
            insert_generated_legal_documents_one(object: $document) {
                id
                template_id
                document_number
                document_type
                title
                content
                variables_used
                status
                client_id
                property_id
                loan_id
                agent_id
                generated_by
                signed_by_client
                signed_by_agent
                signature_client_date
                signature_agent_date
                created_at
                updated_at
            }
        }
        """

        variables = {
            "document": {
                **generation_data.dict(),
                "id": str(uuid4()),
                "document_number": document_number,
                "document_type": template.document_type,
                "content": generated_content,
                "status": LegalDocumentStatus.DRAFT,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        }

        result = await self.client.execute_mutation(mutation, variables)
        return GeneratedLegalDocument(**result["data"]["insert_generated_legal_documents_one"])

    async def get_template_by_id(self, template_id: UUID) -> Optional[LegalDocumentTemplate]:
        """Get a specific template by ID"""
        query = """
        query GetLegalDocumentTemplate($id: uuid!) {
            legal_document_templates_by_pk(id: $id) {
                id
                template_name
                document_type
                version
                content
                variables
                is_active
                created_by
                created_at
                updated_at
            }
        }
        """

        variables = {"id": str(template_id)}
        result = await self.client.execute_query(query, variables)
        template_data = result["data"]["legal_document_templates_by_pk"]
        return LegalDocumentTemplate(**template_data) if template_data else None

    async def generate_document_number(self, document_type: LegalDocumentType) -> str:
        """Generate a unique document number"""
        # Get current year and month
        now = datetime.utcnow()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        
        # Document type prefixes
        prefixes = {
            LegalDocumentType.SALE_CONTRACT: "CV",
            LegalDocumentType.RENTAL_CONTRACT: "AL",
            LegalDocumentType.LOAN_CONTRACT: "PR",
            LegalDocumentType.INTERMEDIATION_CONTRACT: "IN",
            LegalDocumentType.MORTGAGE_CONTRACT: "HIP",
            LegalDocumentType.PROMISSORY_NOTE: "PAG"
        }
        
        prefix = prefixes.get(document_type, "DOC")
        
        # Get count of documents of this type this month
        query = """
        query GetDocumentCount($document_type: String!, $date_start: timestamptz!) {
            generated_legal_documents_aggregate(
                where: {
                    document_type: {_eq: $document_type},
                    created_at: {_gte: $date_start}
                }
            ) {
                aggregate {
                    count
                }
            }
        }
        """
        
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        variables = {
            "document_type": document_type,
            "date_start": month_start.isoformat()
        }
        
        result = await self.client.execute_query(query, variables)
        count = result["data"]["generated_legal_documents_aggregate"]["aggregate"]["count"]
        
        # Format: GI-CV-2024-03-0001
        return f"GI-{prefix}-{year}-{month}-{count + 1:04d}"

    # Document Management
    async def get_generated_documents(self, 
                                    user_id: Optional[UUID] = None, 
                                    document_type: Optional[LegalDocumentType] = None,
                                    status: Optional[LegalDocumentStatus] = None) -> List[GeneratedLegalDocument]:
        """Get generated legal documents with filters"""
        query = """
        query GetGeneratedLegalDocuments($where: generated_legal_documents_bool_exp) {
            generated_legal_documents(where: $where, order_by: {created_at: desc}) {
                id
                template_id
                document_number
                document_type
                title
                content
                variables_used
                status
                client_id
                property_id
                loan_id
                agent_id
                generated_by
                signed_by_client
                signed_by_agent
                signature_client_date
                signature_agent_date
                created_at
                updated_at
            }
        }
        """

        where_clause = {}
        if user_id:
            where_clause["generated_by"] = {"_eq": str(user_id)}
        if document_type:
            where_clause["document_type"] = {"_eq": document_type}
        if status:
            where_clause["status"] = {"_eq": status}

        variables = {"where": where_clause}
        result = await self.client.execute_query(query, variables)
        return [GeneratedLegalDocument(**doc) for doc in result["data"]["generated_legal_documents"]]

    async def update_document_status(self, document_id: UUID, update_data: GeneratedLegalDocumentUpdate) -> Optional[GeneratedLegalDocument]:
        """Update a generated document"""
        mutation = """
        mutation UpdateGeneratedLegalDocument($id: uuid!, $document: generated_legal_documents_set_input!) {
            update_generated_legal_documents_by_pk(pk_columns: {id: $id}, _set: $document) {
                id
                template_id
                document_number
                document_type
                title
                content
                variables_used
                status
                client_id
                property_id
                loan_id
                agent_id
                generated_by
                signed_by_client
                signed_by_agent
                signature_client_date
                signature_agent_date
                created_at
                updated_at
            }
        }
        """

        update_values = {k: v for k, v in update_data.dict().items() if v is not None}
        update_values["updated_at"] = datetime.utcnow().isoformat()

        variables = {
            "id": str(document_id),
            "document": update_values
        }

        result = await self.client.execute_mutation(mutation, variables)
        document_data = result["data"]["update_generated_legal_documents_by_pk"]
        return GeneratedLegalDocument(**document_data) if document_data else None

    # Compliance Audits
    async def create_compliance_audit(self, audit_data: ComplianceAuditCreate) -> ComplianceAudit:
        """Create a new compliance audit"""
        mutation = """
        mutation CreateComplianceAudit($audit: compliance_audits_insert_input!) {
            insert_compliance_audits_one(object: $audit) {
                id
                audit_type
                entity_type
                entity_id
                compliance_status
                findings
                recommendations
                auditor_id
                audit_date
                next_audit_date
                created_at
            }
        }
        """

        variables = {
            "audit": {
                **audit_data.dict(),
                "id": str(uuid4()),
                "audit_date": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
        }

        result = await self.client.execute_mutation(mutation, variables)
        return ComplianceAudit(**result["data"]["insert_compliance_audits_one"])

    # Data Protection
    async def record_consent(self, consent_data: DataProtectionConsentCreate) -> DataProtectionConsent:
        """Record user consent for data protection"""
        mutation = """
        mutation CreateDataProtectionConsent($consent: data_protection_consents_insert_input!) {
            insert_data_protection_consents_one(object: $consent) {
                id
                user_id
                consent_type
                consent_given
                consent_date
                consent_version
                ip_address
                user_agent
                withdrawn_date
                created_at
            }
        }
        """

        variables = {
            "consent": {
                **consent_data.dict(),
                "id": str(uuid4()),
                "consent_date": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
        }

        result = await self.client.execute_mutation(mutation, variables)
        return DataProtectionConsent(**result["data"]["insert_data_protection_consents_one"]) 