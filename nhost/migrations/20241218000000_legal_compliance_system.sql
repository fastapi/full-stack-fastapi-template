-- Migration: Legal Compliance System
-- Date: 2024-12-18
-- Description: Create tables for legal document templates, generated documents, compliance audits, and data protection

-- Legal Document Templates Table
CREATE TABLE legal_document_templates (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    template_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL CHECK (document_type IN (
        'sale_contract', 'rental_contract', 'loan_contract', 'intermediation_contract',
        'privacy_policy', 'terms_conditions', 'mortgage_contract', 'promissory_note'
    )),
    version VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    variables JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_by uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Generated Legal Documents Table
CREATE TABLE generated_legal_documents (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    template_id uuid NOT NULL REFERENCES legal_document_templates(id) ON DELETE CASCADE,
    document_number VARCHAR(50) NOT NULL UNIQUE,
    document_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    variables_used JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'inactive', 'archived')),
    client_id uuid REFERENCES users(id) ON DELETE SET NULL,
    property_id uuid REFERENCES properties(id) ON DELETE SET NULL,
    loan_id uuid REFERENCES loans(id) ON DELETE SET NULL,
    agent_id uuid REFERENCES users(id) ON DELETE SET NULL,
    generated_by uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    signed_by_client BOOLEAN DEFAULT false,
    signed_by_agent BOOLEAN DEFAULT false,
    signature_client_date TIMESTAMPTZ,
    signature_agent_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Compliance Audits Table
CREATE TABLE compliance_audits (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    audit_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id uuid NOT NULL,
    compliance_status VARCHAR(20) NOT NULL CHECK (compliance_status IN ('compliant', 'non_compliant', 'pending_review')),
    findings TEXT[] NOT NULL DEFAULT '{}',
    recommendations TEXT[] NOT NULL DEFAULT '{}',
    auditor_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    audit_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    next_audit_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Data Protection Consents Table
CREATE TABLE data_protection_consents (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    consent_type VARCHAR(50) NOT NULL,
    consent_given BOOLEAN NOT NULL,
    consent_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    consent_version VARCHAR(20) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    withdrawn_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX idx_legal_document_templates_type ON legal_document_templates(document_type);
CREATE INDEX idx_legal_document_templates_active ON legal_document_templates(is_active);
CREATE INDEX idx_legal_document_templates_created_by ON legal_document_templates(created_by);

CREATE INDEX idx_generated_legal_documents_type ON generated_legal_documents(document_type);
CREATE INDEX idx_generated_legal_documents_status ON generated_legal_documents(status);
CREATE INDEX idx_generated_legal_documents_generated_by ON generated_legal_documents(generated_by);
CREATE INDEX idx_generated_legal_documents_client ON generated_legal_documents(client_id);
CREATE INDEX idx_generated_legal_documents_property ON generated_legal_documents(property_id);
CREATE INDEX idx_generated_legal_documents_loan ON generated_legal_documents(loan_id);
CREATE INDEX idx_generated_legal_documents_number ON generated_legal_documents(document_number);

CREATE INDEX idx_compliance_audits_entity ON compliance_audits(entity_type, entity_id);
CREATE INDEX idx_compliance_audits_status ON compliance_audits(compliance_status);
CREATE INDEX idx_compliance_audits_auditor ON compliance_audits(auditor_id);
CREATE INDEX idx_compliance_audits_date ON compliance_audits(audit_date);

CREATE INDEX idx_data_protection_consents_user ON data_protection_consents(user_id);
CREATE INDEX idx_data_protection_consents_type ON data_protection_consents(consent_type);
CREATE INDEX idx_data_protection_consents_date ON data_protection_consents(consent_date);

-- Row Level Security (RLS) Policies
ALTER TABLE legal_document_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_legal_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_audits ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_protection_consents ENABLE ROW LEVEL SECURITY;

-- RLS Policies for legal_document_templates
CREATE POLICY "legal_template_select_policy" ON legal_document_templates
    FOR SELECT USING (
        auth.role() = 'authenticated' AND (
            -- CEO and Managers can see all templates
            auth.jwt() ->> 'role' IN ('ceo', 'manager') OR
            -- Agents can only see active templates
            (auth.jwt() ->> 'role' = 'agent' AND is_active = true)
        )
    );

CREATE POLICY "legal_template_insert_policy" ON legal_document_templates
    FOR INSERT WITH CHECK (
        auth.role() = 'authenticated' AND 
        auth.jwt() ->> 'role' IN ('ceo', 'manager') AND
        created_by = auth.uid()
    );

CREATE POLICY "legal_template_update_policy" ON legal_document_templates
    FOR UPDATE USING (
        auth.role() = 'authenticated' AND 
        auth.jwt() ->> 'role' IN ('ceo', 'manager')
    );

-- RLS Policies for generated_legal_documents
CREATE POLICY "generated_document_select_policy" ON generated_legal_documents
    FOR SELECT USING (
        auth.role() = 'authenticated' AND (
            -- CEO and Managers can see all documents
            auth.jwt() ->> 'role' IN ('ceo', 'manager') OR
            -- Agents can only see their own documents or documents where they are the agent
            (auth.jwt() ->> 'role' = 'agent' AND (generated_by = auth.uid() OR agent_id = auth.uid())) OR
            -- Clients can only see their own documents
            (auth.jwt() ->> 'role' = 'client' AND client_id = auth.uid())
        )
    );

CREATE POLICY "generated_document_insert_policy" ON generated_legal_documents
    FOR INSERT WITH CHECK (
        auth.role() = 'authenticated' AND 
        auth.jwt() ->> 'role' IN ('ceo', 'manager', 'agent') AND
        generated_by = auth.uid()
    );

CREATE POLICY "generated_document_update_policy" ON generated_legal_documents
    FOR UPDATE USING (
        auth.role() = 'authenticated' AND (
            -- CEO and Managers can update any document
            auth.jwt() ->> 'role' IN ('ceo', 'manager') OR
            -- Agents can update their own documents
            (auth.jwt() ->> 'role' = 'agent' AND generated_by = auth.uid())
        )
    );

-- RLS Policies for compliance_audits
CREATE POLICY "compliance_audit_select_policy" ON compliance_audits
    FOR SELECT USING (
        auth.role() = 'authenticated' AND 
        auth.jwt() ->> 'role' IN ('ceo', 'manager')
    );

CREATE POLICY "compliance_audit_insert_policy" ON compliance_audits
    FOR INSERT WITH CHECK (
        auth.role() = 'authenticated' AND 
        auth.jwt() ->> 'role' IN ('ceo', 'manager') AND
        auditor_id = auth.uid()
    );

-- RLS Policies for data_protection_consents
CREATE POLICY "data_protection_consent_select_policy" ON data_protection_consents
    FOR SELECT USING (
        auth.role() = 'authenticated' AND (
            -- CEO and Managers can see all consents
            auth.jwt() ->> 'role' IN ('ceo', 'manager') OR
            -- Users can see their own consents
            user_id = auth.uid()
        )
    );

CREATE POLICY "data_protection_consent_insert_policy" ON data_protection_consents
    FOR INSERT WITH CHECK (
        auth.role() = 'authenticated' AND 
        user_id = auth.uid()
    );

-- Comments for documentation
COMMENT ON TABLE legal_document_templates IS 'Store legal document templates with GENIUS INDUSTRIES branding';
COMMENT ON TABLE generated_legal_documents IS 'Store generated legal documents from templates';
COMMENT ON TABLE compliance_audits IS 'Store compliance audit records for legal and operational compliance';
COMMENT ON TABLE data_protection_consents IS 'Store user consent records for GDPR compliance';

COMMENT ON COLUMN legal_document_templates.variables IS 'JSON object defining template variables and their types';
COMMENT ON COLUMN generated_legal_documents.variables_used IS 'JSON object with actual values used when generating the document';
COMMENT ON COLUMN generated_legal_documents.document_number IS 'Unique document number with format: GI-TYPE-YYYY-MM-NNNN'; 