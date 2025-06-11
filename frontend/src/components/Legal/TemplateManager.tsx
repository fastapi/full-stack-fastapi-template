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
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  IconButton,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  Switch,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  useColorModeValue
} from '@chakra-ui/react';
import {
  FiPlus,
  FiEdit3,
  FiEye,
  FiTrash2,
  FiCopy,
  FiDownload,
  FiUpload,
  FiSettings,
  FiFileText,
  FiCode,
  FiSave,
  FiX
} from 'react-icons/fi';

interface LegalTemplate {
  id: string;
  template_name: string;
  document_type: string;
  version: string;
  content: string;
  variables: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface TemplateFormData {
  template_name: string;
  document_type: string;
  version: string;
  content: string;
  variables: Record<string, any>;
  is_active: boolean;
}

const TemplateManager: React.FC = () => {
  const [templates, setTemplates] = useState<LegalTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<LegalTemplate | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<TemplateFormData>({
    template_name: '',
    document_type: 'sale_contract',
    version: '1.0',
    content: '',
    variables: {},
    is_active: true
  });

  const { isOpen, onOpen, onClose } = useDisclosure();
  const { 
    isOpen: isDeleteOpen, 
    onOpen: onDeleteOpen, 
    onClose: onDeleteClose 
  } = useDisclosure();
  const { 
    isOpen: isPreviewOpen, 
    onOpen: onPreviewOpen, 
    onClose: onPreviewClose 
  } = useDisclosure();
  
  const toast = useToast();
  const cancelRef = React.useRef<HTMLButtonElement>(null);

  // Theme colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    // TODO: Fetch from API
    const mockTemplates: LegalTemplate[] = [
      {
        id: '1',
        template_name: 'Contrato de Compra-Venta Estándar',
        document_type: 'sale_contract',
        version: '1.0',
        content: getDefaultSaleTemplate(),
        variables: {
          seller_name: { type: 'string', required: true, description: 'Nombre del vendedor' },
          buyer_name: { type: 'string', required: true, description: 'Nombre del comprador' },
          property_address: { type: 'string', required: true, description: 'Dirección del inmueble' },
          sale_price: { type: 'number', required: true, description: 'Precio de venta' }
        },
        is_active: true,
        created_at: '2024-12-01',
        updated_at: '2024-12-15'
      },
      {
        id: '2',
        template_name: 'Contrato de Arrendamiento Residencial',
        document_type: 'rental_contract',
        version: '1.1',
        content: getDefaultRentalTemplate(),
        variables: {
          landlord_name: { type: 'string', required: true, description: 'Nombre del arrendador' },
          tenant_name: { type: 'string', required: true, description: 'Nombre del arrendatario' },
          monthly_rent: { type: 'number', required: true, description: 'Canon mensual' }
        },
        is_active: true,
        created_at: '2024-11-15',
        updated_at: '2024-12-10'
      },
      {
        id: '3',
        template_name: 'Contrato de Préstamo Personal',
        document_type: 'loan_contract',
        version: '1.0',
        content: getDefaultLoanTemplate(),
        variables: {
          borrower_name: { type: 'string', required: true, description: 'Nombre del prestatario' },
          loan_amount: { type: 'number', required: true, description: 'Monto del préstamo' },
          interest_rate: { type: 'number', required: true, description: 'Tasa de interés' }
        },
        is_active: false,
        created_at: '2024-10-20',
        updated_at: '2024-11-05'
      }
    ];
    setTemplates(mockTemplates);
  };

  const getDefaultSaleTemplate = () => `
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
      <!-- GENIUS INDUSTRIES Header -->
      <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #000000; padding-bottom: 20px;">
        <div style="width: 200px; height: 80px; background-color: #000000; color: #FFFFFF; 
                   display: inline-block; line-height: 80px; font-weight: bold; font-size: 20px;">
          GENIUS INDUSTRIES
        </div>
        <h1 style="color: #000000; margin: 10px 0;">GENIUS INDUSTRIES</h1>
        <p style="color: #666666; font-size: 12px;">Servicios Inmobiliarios y Financieros</p>
      </div>
      
      <h2 style="text-align: center; color: #000000;">CONTRATO DE COMPRA-VENTA</h2>
      
      <p><strong>VENDEDOR:</strong> {{seller_name}}</p>
      <p><strong>COMPRADOR:</strong> {{buyer_name}}</p>
      <p><strong>INMUEBLE:</strong> {{property_address}}</p>
      <p><strong>PRECIO:</strong> {{currency}} {{sale_price}}</p>
      
      <!-- Footer -->
      <div style="margin-top: 40px; text-align: center; font-size: 10px; color: #999999;">
        <p>GENIUS INDUSTRIES - Documento generado el: {{generation_date}}</p>
      </div>
    </div>
  `;

  const getDefaultRentalTemplate = () => `
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
      <!-- GENIUS INDUSTRIES Header -->
      <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #000000; padding-bottom: 20px;">
        <div style="width: 200px; height: 80px; background-color: #000000; color: #FFFFFF; 
                   display: inline-block; line-height: 80px; font-weight: bold; font-size: 20px;">
          GENIUS INDUSTRIES
        </div>
        <h1 style="color: #000000; margin: 10px 0;">GENIUS INDUSTRIES</h1>
        <p style="color: #666666; font-size: 12px;">Servicios Inmobiliarios y Financieros</p>
      </div>
      
      <h2 style="text-align: center; color: #000000;">CONTRATO DE ARRENDAMIENTO</h2>
      
      <p><strong>ARRENDADOR:</strong> {{landlord_name}}</p>
      <p><strong>ARRENDATARIO:</strong> {{tenant_name}}</p>
      <p><strong>CANON MENSUAL:</strong> {{currency}} {{monthly_rent}}</p>
      
      <!-- Footer -->
      <div style="margin-top: 40px; text-align: center; font-size: 10px; color: #999999;">
        <p>GENIUS INDUSTRIES - Documento generado el: {{generation_date}}</p>
      </div>
    </div>
  `;

  const getDefaultLoanTemplate = () => `
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
      <!-- GENIUS INDUSTRIES Header -->
      <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #000000; padding-bottom: 20px;">
        <div style="width: 200px; height: 80px; background-color: #000000; color: #FFFFFF; 
                   display: inline-block; line-height: 80px; font-weight: bold; font-size: 20px;">
          GENIUS INDUSTRIES
        </div>
        <h1 style="color: #000000; margin: 10px 0;">GENIUS INDUSTRIES</h1>
        <p style="color: #666666; font-size: 12px;">Servicios Inmobiliarios y Financieros</p>
      </div>
      
      <h2 style="text-align: center; color: #000000;">CONTRATO DE PRÉSTAMO</h2>
      
      <p><strong>PRESTAMISTA:</strong> GENIUS INDUSTRIES</p>
      <p><strong>PRESTATARIO:</strong> {{borrower_name}}</p>
      <p><strong>MONTO:</strong> {{currency}} {{loan_amount}}</p>
      <p><strong>TASA:</strong> {{interest_rate}}%</p>
      
      <!-- Footer -->
      <div style="margin-top: 40px; text-align: center; font-size: 10px; color: #999999;">
        <p>GENIUS INDUSTRIES - Documento generado el: {{generation_date}}</p>
      </div>
    </div>
  `;

  const handleCreateNew = () => {
    setIsEditing(false);
    setSelectedTemplate(null);
    setFormData({
      template_name: '',
      document_type: 'sale_contract',
      version: '1.0',
      content: getDefaultSaleTemplate(),
      variables: {},
      is_active: true
    });
    onOpen();
  };

  const handleEdit = (template: LegalTemplate) => {
    setIsEditing(true);
    setSelectedTemplate(template);
    setFormData({
      template_name: template.template_name,
      document_type: template.document_type,
      version: template.version,
      content: template.content,
      variables: template.variables,
      is_active: template.is_active
    });
    onOpen();
  };

  const handleSave = async () => {
    try {
      // TODO: Call API to save template
      toast({
        title: isEditing ? "Template actualizado" : "Template creado",
        description: "El template se ha guardado exitosamente",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      onClose();
      fetchTemplates();
    } catch (error) {
      toast({
        title: "Error",
        description: "No se pudo guardar el template",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleDelete = async () => {
    try {
      // TODO: Call API to delete template
      toast({
        title: "Template eliminado",
        description: "El template se ha eliminado exitosamente",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      onDeleteClose();
      fetchTemplates();
    } catch (error) {
      toast({
        title: "Error",
        description: "No se pudo eliminar el template",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handlePreview = (template: LegalTemplate) => {
    setSelectedTemplate(template);
    onPreviewOpen();
  };

  const getDocumentTypeLabel = (type: string) => {
    const types: Record<string, string> = {
      sale_contract: 'Compra-Venta',
      rental_contract: 'Arrendamiento',
      loan_contract: 'Préstamo',
      intermediation_contract: 'Intermediación',
      mortgage_contract: 'Hipotecario',
      promissory_note: 'Pagaré'
    };
    return types[type] || type;
  };

  const getDocumentTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      sale_contract: 'green',
      rental_contract: 'blue',
      loan_contract: 'purple',
      intermediation_contract: 'orange',
      mortgage_contract: 'red',
      promissory_note: 'teal'
    };
    return colors[type] || 'gray';
  };

  return (
    <Container maxW="7xl" py={8}>
      {/* Header */}
      <Box mb={8}>
        <Flex align="center" justify="space-between" mb={4}>
          <Flex align="center">
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
                Gestión de Templates
              </Heading>
              <Text color="gray.600" fontSize="sm">
                GENIUS INDUSTRIES - Administra plantillas de documentos legales
              </Text>
            </VStack>
          </Flex>
          <Button 
            leftIcon={<Icon as={FiPlus} />}
            bg="black"
            color="white"
            _hover={{ bg: 'gray.800' }}
            onClick={handleCreateNew}
          >
            Nuevo Template
          </Button>
        </Flex>
        <Divider borderColor="black" />
      </Box>

      {/* Stats Cards */}
      <Grid templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }} gap={6} mb={8}>
        <Card border="1px solid" borderColor={borderColor}>
          <CardBody>
            <Flex align="center" justify="space-between">
              <Box>
                <Text color="gray.600" fontSize="sm">Total Templates</Text>
                <Text color="black" fontSize="2xl" fontWeight="bold">
                  {templates.length}
                </Text>
              </Box>
              <Icon as={FiFileText} w={8} h={8} color="black" />
            </Flex>
          </CardBody>
        </Card>
        
        <Card border="1px solid" borderColor={borderColor}>
          <CardBody>
            <Flex align="center" justify="space-between">
              <Box>
                <Text color="gray.600" fontSize="sm">Activos</Text>
                <Text color="black" fontSize="2xl" fontWeight="bold">
                  {templates.filter(t => t.is_active).length}
                </Text>
              </Box>
              <Icon as={FiSettings} w={8} h={8} color="green.500" />
            </Flex>
          </CardBody>
        </Card>
        
        <Card border="1px solid" borderColor={borderColor}>
          <CardBody>
            <Flex align="center" justify="space-between">
              <Box>
                <Text color="gray.600" fontSize="sm">Tipos</Text>
                <Text color="black" fontSize="2xl" fontWeight="bold">
                  {new Set(templates.map(t => t.document_type)).size}
                </Text>
              </Box>
              <Icon as={FiCode} w={8} h={8} color="blue.500" />
            </Flex>
          </CardBody>
        </Card>
        
        <Card border="1px solid" borderColor={borderColor}>
          <CardBody>
            <Flex align="center" justify="space-between">
              <Box>
                <Text color="gray.600" fontSize="sm">Última Actualización</Text>
                <Text color="black" fontSize="sm" fontWeight="bold">
                  Hace 2 días
                </Text>
              </Box>
              <Icon as={FiEdit3} w={8} h={8} color="orange.500" />
            </Flex>
          </CardBody>
        </Card>
      </Grid>

      {/* Templates Table */}
      <Card>
        <CardHeader>
          <Heading size="md" color="black">
            Templates de Documentos
          </Heading>
        </CardHeader>
        <CardBody>
          <Box overflowX="auto">
            <Table variant="simple">
              <Thead>
                <Tr>
                  <Th color="black">Nombre</Th>
                  <Th color="black">Tipo</Th>
                  <Th color="black">Versión</Th>
                  <Th color="black">Estado</Th>
                  <Th color="black">Última Actualización</Th>
                  <Th color="black">Acciones</Th>
                </Tr>
              </Thead>
              <Tbody>
                {templates.map((template) => (
                  <Tr key={template.id}>
                    <Td>
                      <VStack align="start" spacing={0}>
                        <Text fontWeight="semibold" color="black">
                          {template.template_name}
                        </Text>
                        <Text fontSize="sm" color="gray.600">
                          {Object.keys(template.variables).length} variables
                        </Text>
                      </VStack>
                    </Td>
                    <Td>
                      <Badge 
                        colorScheme={getDocumentTypeColor(template.document_type)}
                        variant="subtle"
                      >
                        {getDocumentTypeLabel(template.document_type)}
                      </Badge>
                    </Td>
                    <Td>
                      <Text color="black">v{template.version}</Text>
                    </Td>
                    <Td>
                      <Badge 
                        colorScheme={template.is_active ? 'green' : 'red'}
                        variant="subtle"
                      >
                        {template.is_active ? 'Activo' : 'Inactivo'}
                      </Badge>
                    </Td>
                    <Td>
                      <Text color="gray.600" fontSize="sm">
                        {new Date(template.updated_at).toLocaleDateString()}
                      </Text>
                    </Td>
                    <Td>
                      <HStack spacing={2}>
                        <IconButton
                          aria-label="Ver preview"
                          icon={<Icon as={FiEye} />}
                          size="sm"
                          variant="ghost"
                          color="black"
                          onClick={() => handlePreview(template)}
                        />
                        <IconButton
                          aria-label="Editar"
                          icon={<Icon as={FiEdit3} />}
                          size="sm"
                          variant="ghost"
                          color="black"
                          onClick={() => handleEdit(template)}
                        />
                        <IconButton
                          aria-label="Duplicar"
                          icon={<Icon as={FiCopy} />}
                          size="sm"
                          variant="ghost"
                          color="black"
                        />
                        <IconButton
                          aria-label="Eliminar"
                          icon={<Icon as={FiTrash2} />}
                          size="sm"
                          variant="ghost"
                          color="red.500"
                          onClick={() => {
                            setSelectedTemplate(template);
                            onDeleteOpen();
                          }}
                        />
                      </HStack>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
        </CardBody>
      </Card>

      {/* Create/Edit Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="6xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader color="black">
            {isEditing ? 'Editar Template' : 'Crear Nuevo Template'}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={6} align="stretch">
              <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={4}>
                <FormControl isRequired>
                  <FormLabel color="black">Nombre del Template</FormLabel>
                  <Input 
                    value={formData.template_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, template_name: e.target.value }))}
                    placeholder="Ej: Contrato de Compra-Venta Estándar"
                  />
                </FormControl>
                
                <FormControl isRequired>
                  <FormLabel color="black">Tipo de Documento</FormLabel>
                  <Select 
                    value={formData.document_type}
                    onChange={(e) => setFormData(prev => ({ ...prev, document_type: e.target.value }))}
                  >
                    <option value="sale_contract">Compra-Venta</option>
                    <option value="rental_contract">Arrendamiento</option>
                    <option value="loan_contract">Préstamo</option>
                    <option value="intermediation_contract">Intermediación</option>
                    <option value="mortgage_contract">Hipotecario</option>
                    <option value="promissory_note">Pagaré</option>
                  </Select>
                </FormControl>
                
                <FormControl isRequired>
                  <FormLabel color="black">Versión</FormLabel>
                  <Input 
                    value={formData.version}
                    onChange={(e) => setFormData(prev => ({ ...prev, version: e.target.value }))}
                    placeholder="1.0"
                  />
                </FormControl>
                
                <FormControl display="flex" alignItems="center">
                  <FormLabel color="black" mb="0">
                    Template Activo
                  </FormLabel>
                  <Switch 
                    isChecked={formData.is_active}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                    colorScheme="green"
                  />
                </FormControl>
              </Grid>
              
              <FormControl isRequired>
                <FormLabel color="black">Contenido HTML del Template</FormLabel>
                <Textarea 
                  value={formData.content}
                  onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Contenido HTML con variables {{variable_name}}"
                  rows={15}
                  fontFamily="monospace"
                  fontSize="sm"
                />
                <Text fontSize="xs" color="gray.500" mt={1}>
                  Usa {{variable_name}} para insertar variables dinámicas. El header y footer de GENIUS INDUSTRIES se incluyen automáticamente.
                </Text>
              </FormControl>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancelar
            </Button>
            <Button 
              bg="black" 
              color="white"
              _hover={{ bg: 'gray.800' }}
              leftIcon={<Icon as={FiSave} />}
              onClick={handleSave}
            >
              {isEditing ? 'Actualizar' : 'Crear'} Template
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Preview Modal */}
      <Modal isOpen={isPreviewOpen} onClose={onPreviewClose} size="6xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader color="black">
            Vista Previa: {selectedTemplate?.template_name}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Box 
              border="1px solid" 
              borderColor="gray.200" 
              borderRadius="md" 
              p={6}
              bg="white"
              maxH="600px"
              overflowY="auto"
            >
              <div dangerouslySetInnerHTML={{ __html: selectedTemplate?.content || '' }} />
            </Box>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" onClick={onPreviewClose}>
              Cerrar
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Delete Confirmation */}
      <AlertDialog
        isOpen={isDeleteOpen}
        leastDestructiveRef={cancelRef}
        onClose={onDeleteClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold" color="black">
              Eliminar Template
            </AlertDialogHeader>
            <AlertDialogBody>
              ¿Estás seguro de que quieres eliminar el template "{selectedTemplate?.template_name}"? 
              Esta acción no se puede deshacer.
            </AlertDialogBody>
            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onDeleteClose}>
                Cancelar
              </Button>
              <Button colorScheme="red" onClick={handleDelete} ml={3}>
                Eliminar
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Container>
  );
};

export default TemplateManager; 