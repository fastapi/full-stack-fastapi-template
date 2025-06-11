import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useToast } from '@chakra-ui/react';
import {
  getTemplates,
  getTemplate,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  generateDocument,
  getGeneratedDocuments,
  getGeneratedDocument,
  updateGeneratedDocument,
  deleteGeneratedDocument,
  downloadDocument,
  emailDocument,
  signDocument,
  getComplianceAudits,
  createComplianceAudit,
  createSampleTemplates,
  getLegalStats,
  LegalDocumentTemplate,
  LegalDocumentTemplateCreate,
  LegalDocumentTemplateUpdate,
  GeneratedLegalDocument,
  GeneratedLegalDocumentCreate,
  GeneratedLegalDocumentUpdate,
  ComplianceAudit,
  ComplianceAuditCreate
} from '../client/legalApi';

// Query Keys
export const LEGAL_QUERY_KEYS = {
  templates: ['legal', 'templates'],
  template: (id: string) => ['legal', 'templates', id],
  templatesByType: (type: string) => ['legal', 'templates', 'type', type],
  documents: ['legal', 'documents'],
  document: (id: string) => ['legal', 'documents', id],
  documentsByType: (type: string) => ['legal', 'documents', 'type', type],
  documentsByStatus: (status: string) => ['legal', 'documents', 'status', status],
  audits: ['legal', 'audits'],
  stats: ['legal', 'stats']
} as const;

// Templates Hooks
export const useTemplates = (document_type?: string) => {
  return useQuery({
    queryKey: document_type 
      ? LEGAL_QUERY_KEYS.templatesByType(document_type)
      : LEGAL_QUERY_KEYS.templates,
    queryFn: () => getTemplates(document_type),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useTemplate = (templateId: string) => {
  return useQuery({
    queryKey: LEGAL_QUERY_KEYS.template(templateId),
    queryFn: () => getTemplate(templateId),
    enabled: !!templateId,
  });
};

export const useCreateTemplate = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: createTemplate,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.templates });
      toast({
        title: 'Template creado exitosamente',
        description: `Se ha creado el template "${data.template_name}"`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al crear template',
        description: error.response?.data?.detail || 'No se pudo crear el template',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });
};

export const useUpdateTemplate = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ templateId, templateData }: { templateId: string; templateData: LegalDocumentTemplateUpdate }) =>
      updateTemplate(templateId, templateData),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.templates });
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.template(data.id) });
      toast({
        title: 'Template actualizado',
        description: `Se ha actualizado el template "${data.template_name}"`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al actualizar template',
        description: error.response?.data?.detail || 'No se pudo actualizar el template',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });
};

export const useDeleteTemplate = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: deleteTemplate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.templates });
      toast({
        title: 'Template eliminado',
        description: 'El template se ha eliminado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al eliminar template',
        description: error.response?.data?.detail || 'No se pudo eliminar el template',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });
};

// Generated Documents Hooks
export const useGeneratedDocuments = (document_type?: string, status?: string) => {
  return useQuery({
    queryKey: document_type || status 
      ? [...LEGAL_QUERY_KEYS.documents, document_type, status].filter(Boolean)
      : LEGAL_QUERY_KEYS.documents,
    queryFn: () => getGeneratedDocuments(document_type, status),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

export const useGeneratedDocument = (documentId: string) => {
  return useQuery({
    queryKey: LEGAL_QUERY_KEYS.document(documentId),
    queryFn: () => getGeneratedDocument(documentId),
    enabled: !!documentId,
  });
};

export const useGenerateDocument = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: generateDocument,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.documents });
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.stats });
      toast({
        title: 'Documento generado exitosamente',
        description: `Se ha generado el documento "${data.document_number}"`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al generar documento',
        description: error.response?.data?.detail || 'No se pudo generar el documento',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });
};

export const useUpdateDocument = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ documentId, documentData }: { documentId: string; documentData: GeneratedLegalDocumentUpdate }) =>
      updateGeneratedDocument(documentId, documentData),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.documents });
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.document(data.id) });
      toast({
        title: 'Documento actualizado',
        description: `Se ha actualizado el documento "${data.document_number}"`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al actualizar documento',
        description: error.response?.data?.detail || 'No se pudo actualizar el documento',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });
};

export const useDeleteDocument = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: deleteGeneratedDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.documents });
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.stats });
      toast({
        title: 'Documento eliminado',
        description: 'El documento se ha eliminado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al eliminar documento',
        description: error.response?.data?.detail || 'No se pudo eliminar el documento',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });
};

// Document Actions Hooks
export const useDownloadDocument = () => {
  const toast = useToast();

  return useMutation({
    mutationFn: downloadDocument,
    onSuccess: (blob, documentId) => {
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `documento-${documentId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast({
        title: 'Descarga iniciada',
        description: 'El documento se está descargando',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error en descarga',
        description: error.response?.data?.detail || 'No se pudo descargar el documento',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });
};

export const useEmailDocument = () => {
  const toast = useToast();

  return useMutation({
    mutationFn: ({ documentId, email, message }: { documentId: string; email: string; message?: string }) =>
      emailDocument(documentId, email, message),
    onSuccess: () => {
      toast({
        title: 'Email enviado',
        description: 'El documento se ha enviado por email exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al enviar email',
        description: error.response?.data?.detail || 'No se pudo enviar el email',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });
};

export const useSignDocument = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: ({ documentId, signatureType }: { documentId: string; signatureType: 'client' | 'agent' }) =>
      signDocument(documentId, signatureType),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.documents });
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.document(data.id) });
      toast({
        title: 'Documento firmado',
        description: 'La firma se ha registrado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al firmar documento',
        description: error.response?.data?.detail || 'No se pudo registrar la firma',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });
};

// Compliance Audits Hooks
export const useComplianceAudits = () => {
  return useQuery({
    queryKey: LEGAL_QUERY_KEYS.audits,
    queryFn: getComplianceAudits,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useCreateComplianceAudit = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: createComplianceAudit,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.audits });
      toast({
        title: 'Auditoría creada',
        description: 'La auditoría de cumplimiento se ha creado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al crear auditoría',
        description: error.response?.data?.detail || 'No se pudo crear la auditoría',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });
};

// Sample Templates Hook
export const useCreateSampleTemplates = () => {
  const queryClient = useQueryClient();
  const toast = useToast();

  return useMutation({
    mutationFn: createSampleTemplates,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: LEGAL_QUERY_KEYS.templates });
      toast({
        title: 'Templates de muestra creados',
        description: `Se han creado ${data.templates.length} templates de ejemplo`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error al crear templates de muestra',
        description: error.response?.data?.detail || 'No se pudieron crear los templates',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });
};

// Legal Stats Hook
export const useLegalStats = () => {
  return useQuery({
    queryKey: LEGAL_QUERY_KEYS.stats,
    queryFn: getLegalStats,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
  });
};

// Utility Hooks
export const useLegalFilters = () => {
  const documentTypes = [
    { value: 'all', label: 'Todos los tipos' },
    { value: 'sale_contract', label: 'Compra-Venta' },
    { value: 'rental_contract', label: 'Arrendamiento' },
    { value: 'loan_contract', label: 'Préstamo' },
    { value: 'intermediation_contract', label: 'Intermediación' },
    { value: 'mortgage_contract', label: 'Hipotecario' },
    { value: 'promissory_note', label: 'Pagaré' },
  ];

  const statusOptions = [
    { value: 'all', label: 'Todos los estados' },
    { value: 'draft', label: 'Borradores' },
    { value: 'active', label: 'Activos' },
    { value: 'signed', label: 'Firmados' },
    { value: 'archived', label: 'Archivados' },
  ];

  return {
    documentTypes,
    statusOptions,
  };
};

// Permission Hook
export const useLegalPermissions = () => {
  // TODO: Get user role from auth context
  const userRole = 'ceo'; // Mock role

  const canCreateTemplate = ['ceo', 'manager'].includes(userRole);
  const canEditTemplate = ['ceo', 'manager'].includes(userRole);
  const canDeleteTemplate = ['ceo'].includes(userRole);
  const canGenerateDocument = ['ceo', 'manager', 'agent'].includes(userRole);
  const canViewAllDocuments = ['ceo', 'manager'].includes(userRole);
  const canCreateAudit = ['ceo', 'manager'].includes(userRole);

  return {
    canCreateTemplate,
    canEditTemplate,
    canDeleteTemplate,
    canGenerateDocument,
    canViewAllDocuments,
    canCreateAudit,
  };
};

export default {
  useTemplates,
  useTemplate,
  useCreateTemplate,
  useUpdateTemplate,
  useDeleteTemplate,
  useGeneratedDocuments,
  useGeneratedDocument,
  useGenerateDocument,
  useUpdateDocument,
  useDeleteDocument,
  useDownloadDocument,
  useEmailDocument,
  useSignDocument,
  useComplianceAudits,
  useCreateComplianceAudit,
  useCreateSampleTemplates,
  useLegalStats,
  useLegalFilters,
  useLegalPermissions,
}; 