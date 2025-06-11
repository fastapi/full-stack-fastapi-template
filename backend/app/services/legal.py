from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import re
from jinja2 import Template

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

    # Corporate Branding - GENIUS INDUSTRIES
    COMPANY_INFO = {
        "name": "GENIUS INDUSTRIES",
        "address": "Dirección Corporativa, Ciudad",
        "phone": "+1 (555) 123-4567",
        "email": "info@genius-industries.com",
        "website": "www.genius-industries.com",
        "tax_id": "12345678-9"
    }

    def get_document_header(self) -> str:
        """Generate corporate header with logo for all documents"""
        return f"""
        <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #000000; padding-bottom: 20px;">
            <div style="margin-bottom: 15px;">
                <!-- LOGO PLACEHOLDER - Replace with actual logo -->
                <div style="width: 150px; height: 60px; background-color: #000000; color: #FFFFFF; 
                           display: inline-block; line-height: 60px; font-weight: bold; font-size: 18px;">
                    GENIUS INDUSTRIES
                </div>
            </div>
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
            <p>Documento generado el: {{{{generation_date}}}}</p>
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

    async def generate_document_number(self, document_type: LegalDocumentType) -> str:
        """Generate a unique document number"""
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
        
        # Simple counter for now (can be enhanced with database query)
        import random
        counter = random.randint(1, 9999)
        
        # Format: GI-CV-2024-03-0001
        return f"GI-{prefix}-{year}-{month}-{counter:04d}"

    # Document Generation
    async def generate_document(self, generation_data: GeneratedLegalDocumentCreate) -> GeneratedLegalDocument:
        """Generate a legal document from a template"""
        # Get template (simplified for now)
        template_content = self.get_sample_template(generation_data.template_id)
        
        # Generate document content using Jinja2
        template_obj = Template(template_content)
        
        # Add corporate info and generation date to variables
        variables_with_corporate = {
            **generation_data.variables_used,
            **self.COMPANY_INFO,
            "generation_date": datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
        }
        
        generated_content = template_obj.render(**variables_with_corporate)

        # Generate unique document number
        document_number = await self.generate_document_number(LegalDocumentType.SALE_CONTRACT)

        # Create document record
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
                "document_type": LegalDocumentType.SALE_CONTRACT,
                "content": generated_content,
                "status": LegalDocumentStatus.DRAFT,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        }

        result = await self.client.execute_mutation(mutation, variables)
        return GeneratedLegalDocument(**result["data"]["insert_generated_legal_documents_one"])

    def get_sample_template(self, template_id: UUID) -> str:
        """Get sample template - will be replaced with database query"""
        return self.get_document_header() + """
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #000000; max-width: 800px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #000000; text-align: center; margin-bottom: 30px;">CONTRATO DE COMPRA-VENTA</h2>
            
            <p><strong>Documento N°:</strong> {{document_number}}</p>
            <p><strong>Fecha:</strong> {{generation_date}}</p>
            
            <h3>PARTES</h3>
            <p><strong>VENDEDOR:</strong> {{seller_name}}, identificado con {{seller_id}}, domiciliado en {{seller_address}}.</p>
            <p><strong>COMPRADOR:</strong> {{buyer_name}}, identificado con {{buyer_id}}, domiciliado en {{buyer_address}}.</p>
            
            <h3>OBJETO DEL CONTRATO</h3>
            <p>El vendedor vende al comprador el inmueble ubicado en {{property_address}}, 
            con las siguientes características:</p>
            <ul>
                <li>Área: {{property_area}} metros cuadrados</li>
                <li>Tipo: {{property_type}}</li>
                <li>Matrícula inmobiliaria: {{property_registry}}</li>
            </ul>
            
            <h3>PRECIO Y FORMA DE PAGO</h3>
            <p>El precio total de la venta es de <strong>{{currency}} {{sale_price}}</strong> ({{sale_price_words}}).</p>
            <p>Forma de pago: {{payment_method}}</p>
            
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
        """ + self.get_document_footer()

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