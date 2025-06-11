import axios, { AxiosResponse } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API Client instance
const legalApi = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/legal`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
legalApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
legalApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login if unauthorized
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface LegalDocumentTemplate {
  id: string;
  template_name: string;
  document_type: string;
  version: string;
  content: string;
  variables: Record<string, any>;
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface LegalDocumentTemplateCreate {
  template_name: string;
  document_type: string;
  version: string;
  content: string;
  variables: Record<string, any>;
}

export interface LegalDocumentTemplateUpdate {
  template_name?: string;
  content?: string;
  variables?: Record<string, any>;
  is_active?: boolean;
}

export interface GeneratedLegalDocument {
  id: string;
  template_id: string;
  document_number: string;
  document_type: string;
  title: string;
  content: string;
  variables_used: Record<string, any>;
  status: 'draft' | 'active' | 'inactive' | 'archived';
  client_id?: string;
  property_id?: string;
  loan_id?: string;
  agent_id?: string;
  generated_by: string;
  signed_by_client: boolean;
  signed_by_agent: boolean;
  signature_client_date?: string;
  signature_agent_date?: string;
  created_at: string;
  updated_at: string;
}

export interface GeneratedLegalDocumentCreate {
  template_id: string;
  title: string;
  variables_used: Record<string, any>;
  client_id?: string;
  property_id?: string;
  loan_id?: string;
  agent_id?: string;
}

export interface GeneratedLegalDocumentUpdate {
  title?: string;
  status?: 'draft' | 'active' | 'inactive' | 'archived';
  signed_by_client?: boolean;
  signed_by_agent?: boolean;
}

export interface ComplianceAudit {
  id: string;
  audit_type: string;
  entity_type: string;
  entity_id: string;
  compliance_status: 'compliant' | 'non_compliant' | 'pending_review';
  findings: string[];
  recommendations: string[];
  auditor_id: string;
  audit_date: string;
  next_audit_date?: string;
  created_at: string;
}

export interface ComplianceAuditCreate {
  audit_type: string;
  entity_type: string;
  entity_id: string;
  compliance_status: 'compliant' | 'non_compliant' | 'pending_review';
  findings: string[];
  recommendations: string[];
  next_audit_date?: string;
}

// API Functions

// Templates
export const getTemplates = async (document_type?: string): Promise<LegalDocumentTemplate[]> => {
  const params = document_type ? { document_type } : {};
  const response: AxiosResponse<LegalDocumentTemplate[]> = await legalApi.get('/templates', { params });
  return response.data;
};

export const getTemplate = async (templateId: string): Promise<LegalDocumentTemplate> => {
  const response: AxiosResponse<LegalDocumentTemplate> = await legalApi.get(`/templates/${templateId}`);
  return response.data;
};

export const createTemplate = async (templateData: LegalDocumentTemplateCreate): Promise<LegalDocumentTemplate> => {
  const response: AxiosResponse<LegalDocumentTemplate> = await legalApi.post('/templates', templateData);
  return response.data;
};

export const updateTemplate = async (
  templateId: string, 
  templateData: LegalDocumentTemplateUpdate
): Promise<LegalDocumentTemplate> => {
  const response: AxiosResponse<LegalDocumentTemplate> = await legalApi.put(`/templates/${templateId}`, templateData);
  return response.data;
};

export const deleteTemplate = async (templateId: string): Promise<void> => {
  await legalApi.delete(`/templates/${templateId}`);
};

// Generated Documents
export const generateDocument = async (documentData: GeneratedLegalDocumentCreate): Promise<GeneratedLegalDocument> => {
  const response: AxiosResponse<GeneratedLegalDocument> = await legalApi.post('/documents/generate', documentData);
  return response.data;
};

export const getGeneratedDocuments = async (
  document_type?: string,
  status?: string
): Promise<GeneratedLegalDocument[]> => {
  const params: any = {};
  if (document_type) params.document_type = document_type;
  if (status) params.status_filter = status;
  
  const response: AxiosResponse<GeneratedLegalDocument[]> = await legalApi.get('/documents', { params });
  return response.data;
};

export const getGeneratedDocument = async (documentId: string): Promise<GeneratedLegalDocument> => {
  const response: AxiosResponse<GeneratedLegalDocument> = await legalApi.get(`/documents/${documentId}`);
  return response.data;
};

export const updateGeneratedDocument = async (
  documentId: string, 
  documentData: GeneratedLegalDocumentUpdate
): Promise<GeneratedLegalDocument> => {
  const response: AxiosResponse<GeneratedLegalDocument> = await legalApi.put(`/documents/${documentId}`, documentData);
  return response.data;
};

export const deleteGeneratedDocument = async (documentId: string): Promise<void> => {
  await legalApi.delete(`/documents/${documentId}`);
};

// Document Actions
export const downloadDocument = async (documentId: string): Promise<Blob> => {
  const response: AxiosResponse<Blob> = await legalApi.get(`/documents/${documentId}/download`, {
    responseType: 'blob'
  });
  return response.data;
};

export const emailDocument = async (documentId: string, email: string, message?: string): Promise<void> => {
  await legalApi.post(`/documents/${documentId}/email`, { email, message });
};

export const signDocument = async (documentId: string, signatureType: 'client' | 'agent'): Promise<GeneratedLegalDocument> => {
  const response: AxiosResponse<GeneratedLegalDocument> = await legalApi.post(`/documents/${documentId}/sign`, {
    signature_type: signatureType
  });
  return response.data;
};

// Compliance Audits
export const getComplianceAudits = async (): Promise<ComplianceAudit[]> => {
  const response: AxiosResponse<ComplianceAudit[]> = await legalApi.get('/audits');
  return response.data;
};

export const createComplianceAudit = async (auditData: ComplianceAuditCreate): Promise<ComplianceAudit> => {
  const response: AxiosResponse<ComplianceAudit> = await legalApi.post('/audits', auditData);
  return response.data;
};

// Sample Templates
export const createSampleTemplates = async (): Promise<{ message: string; templates: string[] }> => {
  const response: AxiosResponse<{ message: string; templates: string[] }> = await legalApi.post('/templates/samples');
  return response.data;
};

// Statistics
export const getLegalStats = async (): Promise<{
  total_documents: number;
  active_templates: number;
  documents_this_month: number;
  pending_signatures: number;
}> => {
  const response = await legalApi.get('/stats');
  return response.data;
};

// Document Types
export const getDocumentTypes = (): { value: string; label: string; description: string }[] => {
  return [
    {
      value: 'sale_contract',
      label: 'Contrato de Compra-Venta',
      description: 'Contrato para la venta de inmuebles'
    },
    {
      value: 'rental_contract',
      label: 'Contrato de Arrendamiento',
      description: 'Contrato para el alquiler de propiedades'
    },
    {
      value: 'loan_contract',
      label: 'Contrato de Préstamo',
      description: 'Contrato para préstamos personales'
    },
    {
      value: 'intermediation_contract',
      label: 'Contrato de Intermediación',
      description: 'Contrato de servicios inmobiliarios'
    },
    {
      value: 'mortgage_contract',
      label: 'Contrato Hipotecario',
      description: 'Contrato para préstamos hipotecarios'
    },
    {
      value: 'promissory_note',
      label: 'Pagaré',
      description: 'Documento de compromiso de pago'
    },
    {
      value: 'privacy_policy',
      label: 'Política de Privacidad',
      description: 'Política de protección de datos'
    },
    {
      value: 'terms_conditions',
      label: 'Términos y Condiciones',
      description: 'Términos de uso de servicios'
    }
  ];
};

// Utility Functions
export const formatDocumentNumber = (type: string, date: Date = new Date()): string => {
  const prefixes: Record<string, string> = {
    sale_contract: 'CV',
    rental_contract: 'AL',
    loan_contract: 'PR',
    intermediation_contract: 'IN',
    mortgage_contract: 'HIP',
    promissory_note: 'PAG',
    privacy_policy: 'POL',
    terms_conditions: 'TER'
  };

  const prefix = prefixes[type] || 'DOC';
  const year = date.getFullYear();
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const counter = Math.floor(Math.random() * 9999) + 1;

  return `GI-${prefix}-${year}-${month}-${counter.toString().padStart(4, '0')}`;
};

export const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    draft: 'yellow',
    active: 'blue',
    signed: 'green',
    archived: 'gray',
    inactive: 'red'
  };
  return colors[status] || 'gray';
};

export const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    draft: 'Borrador',
    active: 'Activo',
    signed: 'Firmado',
    archived: 'Archivado',
    inactive: 'Inactivo'
  };
  return labels[status] || status;
};

export default legalApi; 