import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Grid,
  Card,
  CardBody,
  CardHeader,
  Button,
  Icon,
  Flex,
  VStack,
  HStack,
  Divider,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  NumberInput,
  NumberInputField,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Badge,
  Stepper,
  Step,
  StepIndicator,
  StepStatus,
  StepIcon,
  StepNumber,
  StepTitle,
  StepDescription,
  StepSeparator,
  useSteps
} from '@chakra-ui/react';
import {
  FiFileText,
  FiEdit3,
  FiEye,
  FiDownload,
  FiSave,
  FiArrowLeft,
  FiArrowRight,
  FiCheck,
  FiUser,
  FiHome,
  FiDollarSign
} from 'react-icons/fi';

interface DocumentTemplate {
  id: string;
  template_name: string;
  document_type: string;
  version: string;
  variables: Record<string, any>;
}

interface DocumentFormData {
  template_id: string;
  title: string;
  variables_used: Record<string, any>;
  client_id?: string;
  property_id?: string;
  loan_id?: string;
}

const DocumentGenerator: React.FC = () => {
  const [templates, setTemplates] = useState<DocumentTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<DocumentTemplate | null>(null);
  const [formData, setFormData] = useState<DocumentFormData>({
    template_id: '',
    title: '',
    variables_used: {}
  });
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDocument, setGeneratedDocument] = useState<any>(null);

  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  const steps = [
    { title: 'Seleccionar Template', description: 'Elige el tipo de documento' },
    { title: 'Completar Datos', description: 'Llena la información requerida' },
    { title: 'Vista Previa', description: 'Revisa el documento generado' },
    { title: 'Finalizar', description: 'Guarda y descarga el documento' }
  ];

  const { activeStep, setActiveStep } = useSteps({
    index: 0,
    count: steps.length,
  });

  useEffect(() => {
    // TODO: Fetch templates from API
    setTemplates([
      {
        id: '1',
        template_name: 'Contrato de Compra-Venta Inmobiliaria',
        document_type: 'sale_contract',
        version: '1.0',
        variables: {
          seller_name: { type: 'string', required: true, description: 'Nombre del vendedor' },
          seller_id: { type: 'string', required: true, description: 'ID del vendedor' },
          buyer_name: { type: 'string', required: true, description: 'Nombre del comprador' },
          buyer_id: { type: 'string', required: true, description: 'ID del comprador' },
          property_address: { type: 'string', required: true, description: 'Dirección del inmueble' },
          sale_price: { type: 'number', required: true, description: 'Precio de venta' },
          currency: { type: 'string', required: true, description: 'Moneda' }
        }
      },
      {
        id: '2',
        template_name: 'Contrato de Arrendamiento',
        document_type: 'rental_contract',
        version: '1.0',
        variables: {
          landlord_name: { type: 'string', required: true, description: 'Nombre del arrendador' },
          tenant_name: { type: 'string', required: true, description: 'Nombre del arrendatario' },
          property_address: { type: 'string', required: true, description: 'Dirección del inmueble' },
          monthly_rent: { type: 'number', required: true, description: 'Canon mensual' },
          security_deposit: { type: 'number', required: true, description: 'Depósito' }
        }
      },
      {
        id: '3',
        template_name: 'Contrato de Préstamo Personal',
        document_type: 'loan_contract',
        version: '1.0',
        variables: {
          borrower_name: { type: 'string', required: true, description: 'Nombre del prestatario' },
          borrower_id: { type: 'string', required: true, description: 'ID del prestatario' },
          loan_amount: { type: 'number', required: true, description: 'Monto del préstamo' },
          interest_rate: { type: 'number', required: true, description: 'Tasa de interés' },
          loan_term: { type: 'number', required: true, description: 'Plazo en meses' }
        }
      }
    ]);
  }, []);

  const handleTemplateSelect = (template: DocumentTemplate) => {
    setSelectedTemplate(template);
    setFormData({
      template_id: template.id,
      title: `${template.template_name} - ${new Date().toLocaleDateString()}`,
      variables_used: {}
    });
    setActiveStep(1);
  };

  const handleInputChange = (variableName: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      variables_used: {
        ...prev.variables_used,
        [variableName]: value
      }
    }));
  };

  const handleGenerateDocument = async () => {
    setIsGenerating(true);
    try {
      // TODO: Call API to generate document
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate API call
      
      const mockDocument = {
        id: 'doc-' + Date.now(),
        document_number: `GI-CV-2024-12-${Math.floor(Math.random() * 1000).toString().padStart(4, '0')}`,
        title: formData.title,
        content: generatePreviewContent(),
        status: 'draft'
      };
      
      setGeneratedDocument(mockDocument);
      setActiveStep(3);
      
      toast({
        title: "Documento generado exitosamente",
        description: "El documento está listo para revisión",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: "Error al generar documento",
        description: "No se pudo generar el documento. Intenta nuevamente.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const generatePreviewContent = () => {
    if (!selectedTemplate) return '';
    
    return `
      <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <!-- GENIUS INDUSTRIES Header -->
        <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #000000; padding-bottom: 20px;">
          <div style="width: 200px; height: 80px; background-color: #000000; color: #FFFFFF; 
                     display: inline-block; line-height: 80px; font-weight: bold; font-size: 20px;">
            GENIUS INDUSTRIES
          </div>
          <h1 style="color: #000000; margin: 10px 0; font-size: 24px;">GENIUS INDUSTRIES</h1>
          <p style="color: #666666; font-size: 12px;">
            Servicios Inmobiliarios y Financieros | Tel: +1 (555) 123-4567 | info@genius-industries.com
          </p>
        </div>
        
        <h2 style="text-align: center; color: #000000; text-transform: uppercase;">
          ${selectedTemplate.template_name}
        </h2>
        
        <div style="background-color: #F5F5F5; padding: 15px; margin: 20px 0; border-left: 4px solid #000000;">
          <p><strong>Documento N°:</strong> ${generatedDocument?.document_number || 'GI-XXX-2024-12-XXXX'}</p>
          <p><strong>Fecha:</strong> ${new Date().toLocaleDateString()}</p>
        </div>
        
        <!-- Document content based on variables -->
        ${Object.entries(formData.variables_used).map(([key, value]) => `
          <p><strong>${key.replace(/_/g, ' ').toUpperCase()}:</strong> ${value}</p>
        `).join('')}
        
        <!-- Footer -->
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #E5E5E5; text-align: center; font-size: 10px; color: #999999;">
          <p>GENIUS INDUSTRIES - www.genius-industries.com</p>
          <p>Este documento ha sido generado electrónicamente por GENIUS INDUSTRIES</p>
          <p>Documento generado el: ${new Date().toLocaleString()}</p>
        </div>
      </div>
    `;
  };

  const renderTemplateSelection = () => (
    <VStack spacing={6} align="stretch">
      <Box textAlign="center">
        <Heading size="lg" color="black" mb={2}>
          Seleccionar Tipo de Documento
        </Heading>
        <Text color="gray.600">
          Elige el template que necesitas para generar tu documento legal
        </Text>
      </Box>
      
      <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={6}>
        {templates.map((template) => (
          <Card 
            key={template.id}
            cursor="pointer"
            onClick={() => handleTemplateSelect(template)}
            _hover={{ 
              borderColor: 'black',
              transform: 'translateY(-2px)',
              transition: 'all 0.2s',
              shadow: 'md'
            }}
            border="1px solid"
            borderColor="gray.200"
          >
            <CardBody p={6}>
              <VStack spacing={4} align="center">
                <Icon 
                  as={FiFileText} 
                  w={12} 
                  h={12} 
                  color="black" 
                />
                <VStack spacing={2} textAlign="center">
                  <Heading size="md" color="black">
                    {template.template_name}
                  </Heading>
                  <Badge colorScheme="gray" variant="subtle">
                    v{template.version}
                  </Badge>
                  <Text fontSize="sm" color="gray.600">
                    {Object.keys(template.variables).length} campos requeridos
                  </Text>
                </VStack>
                <Button 
                  size="sm" 
                  bg="black" 
                  color="white"
                  _hover={{ bg: 'gray.800' }}
                  width="full"
                >
                  Seleccionar
                </Button>
              </VStack>
            </CardBody>
          </Card>
        ))}
      </Grid>
    </VStack>
  );

  const renderFormFields = () => {
    if (!selectedTemplate) return null;

    return (
      <VStack spacing={6} align="stretch">
        <Box textAlign="center">
          <Heading size="lg" color="black" mb={2}>
            Completar Información del Documento
          </Heading>
          <Text color="gray.600">
            Llena todos los campos requeridos para generar el {selectedTemplate.template_name}
          </Text>
        </Box>

        <Card>
          <CardHeader>
            <Heading size="md" color="black">
              Información General
            </Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <FormControl isRequired>
                <FormLabel color="black">Título del Documento</FormLabel>
                <Input 
                  value={formData.title}
                  onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Ingresa un título descriptivo"
                />
              </FormControl>
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md" color="black">
              Datos del Documento
            </Heading>
          </CardHeader>
          <CardBody>
            <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
              {Object.entries(selectedTemplate.variables).map(([variableName, variableConfig]: [string, any]) => (
                <FormControl key={variableName} isRequired={variableConfig.required}>
                  <FormLabel color="black">
                    {variableConfig.description || variableName.replace(/_/g, ' ').toUpperCase()}
                  </FormLabel>
                  {variableConfig.type === 'number' ? (
                    <NumberInput>
                      <NumberInputField 
                        onChange={(e) => handleInputChange(variableName, Number(e.target.value))}
                        placeholder={`Ingresa ${variableConfig.description || variableName}`}
                      />
                    </NumberInput>
                  ) : variableConfig.type === 'select' ? (
                    <Select 
                      placeholder={`Selecciona ${variableConfig.description || variableName}`}
                      onChange={(e) => handleInputChange(variableName, e.target.value)}
                    >
                      {variableConfig.options?.map((option: string) => (
                        <option key={option} value={option}>{option}</option>
                      ))}
                    </Select>
                  ) : variableConfig.type === 'textarea' ? (
                    <Textarea 
                      onChange={(e) => handleInputChange(variableName, e.target.value)}
                      placeholder={`Ingresa ${variableConfig.description || variableName}`}
                      rows={3}
                    />
                  ) : (
                    <Input 
                      onChange={(e) => handleInputChange(variableName, e.target.value)}
                      placeholder={`Ingresa ${variableConfig.description || variableName}`}
                    />
                  )}
                </FormControl>
              ))}
            </Grid>
          </CardBody>
        </Card>
      </VStack>
    );
  };

  const renderPreview = () => (
    <VStack spacing={6} align="stretch">
      <Box textAlign="center">
        <Heading size="lg" color="black" mb={2}>
          Vista Previa del Documento
        </Heading>
        <Text color="gray.600">
          Revisa el documento antes de finalizarlo
        </Text>
      </Box>

      <Card>
        <CardHeader>
          <Flex justify="space-between" align="center">
            <Heading size="md" color="black">
              {generatedDocument?.title}
            </Heading>
            <Badge colorScheme="blue" variant="subtle">
              {generatedDocument?.document_number}
            </Badge>
          </Flex>
        </CardHeader>
        <CardBody>
          <Box 
            border="1px solid" 
            borderColor="gray.200" 
            borderRadius="md" 
            p={4}
            bg="white"
            maxH="500px"
            overflowY="auto"
          >
            <div dangerouslySetInnerHTML={{ __html: generatePreviewContent() }} />
          </Box>
        </CardBody>
      </Card>
    </VStack>
  );

  return (
    <Container maxW="6xl" py={8}>
      {/* Header */}
      <Box mb={8}>
        <Flex align="center" mb={4}>
          <Box 
            w={12} 
            h={12} 
            bg="black" 
            color="white" 
            display="flex" 
            alignItems="center" 
            justifyContent="center" 
            mr={4}
            fontWeight="bold"
            fontSize="sm"
          >
            GI
          </Box>
          <VStack align="start" spacing={0}>
            <Heading size="lg" color="black">
              Generador de Documentos
            </Heading>
            <Text color="gray.600" fontSize="sm">
              GENIUS INDUSTRIES - Crea documentos legales profesionales
            </Text>
          </VStack>
        </Flex>
        <Divider borderColor="black" />
      </Box>

      {/* Progress Stepper */}
      <Box mb={8}>
        <Stepper size="lg" index={activeStep}>
          {steps.map((step, index) => (
            <Step key={index}>
              <StepIndicator>
                <StepStatus
                  complete={<StepIcon />}
                  incomplete={<StepNumber />}
                  active={<StepNumber />}
                />
              </StepIndicator>
              <Box flexShrink="0">
                <StepTitle>{step.title}</StepTitle>
                <StepDescription>{step.description}</StepDescription>
              </Box>
              <StepSeparator />
            </Step>
          ))}
        </Stepper>
      </Box>

      {/* Content based on active step */}
      <Box mb={8}>
        {activeStep === 0 && renderTemplateSelection()}
        {activeStep === 1 && renderFormFields()}
        {activeStep === 2 && renderPreview()}
        {activeStep === 3 && renderPreview()}
      </Box>

      {/* Navigation Buttons */}
      <Flex justify="space-between" align="center">
        <Button 
          leftIcon={<Icon as={FiArrowLeft} />}
          variant="outline"
          borderColor="black"
          color="black"
          _hover={{ bg: 'black', color: 'white' }}
          onClick={() => setActiveStep(prev => Math.max(0, prev - 1))}
          isDisabled={activeStep === 0}
        >
          Anterior
        </Button>

        <HStack spacing={4}>
          {activeStep === 1 && (
            <Button 
              rightIcon={<Icon as={FiEye} />}
              bg="black"
              color="white"
              _hover={{ bg: 'gray.800' }}
              onClick={handleGenerateDocument}
              isLoading={isGenerating}
              loadingText="Generando..."
            >
              Generar Vista Previa
            </Button>
          )}

          {activeStep === 2 && (
            <Button 
              rightIcon={<Icon as={FiArrowRight} />}
              bg="black"
              color="white"
              _hover={{ bg: 'gray.800' }}
              onClick={() => setActiveStep(3)}
            >
              Continuar
            </Button>
          )}

          {activeStep === 3 && (
            <HStack spacing={2}>
              <Button 
                leftIcon={<Icon as={FiSave} />}
                bg="black"
                color="white"
                _hover={{ bg: 'gray.800' }}
              >
                Guardar Documento
              </Button>
              <Button 
                leftIcon={<Icon as={FiDownload} />}
                variant="outline"
                borderColor="black"
                color="black"
                _hover={{ bg: 'black', color: 'white' }}
              >
                Descargar PDF
              </Button>
            </HStack>
          )}
        </HStack>
      </Flex>
    </Container>
  );
};

export default DocumentGenerator; 