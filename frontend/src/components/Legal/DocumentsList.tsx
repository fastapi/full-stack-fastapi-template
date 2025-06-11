import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Grid,
  Card,
  CardBody,
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
  Input,
  Select,
  InputGroup,
  InputLeftElement,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useColorModeValue,
  Tooltip,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay
} from '@chakra-ui/react';
import {
  FiFileText,
  FiEye,
  FiDownload,
  FiEdit3,
  FiTrash2,
  FiSearch,
  FiFilter,
  FiMoreVertical,
  FiCopy,
  FiSend,
  FiClock,
  FiCheckCircle,
  FiXCircle,
  FiArchive,
  FiCalendar,
  FiUser,
  FiHome
} from 'react-icons/fi';

interface GeneratedDocument {
  id: string;
  document_number: string;
  template_name: string;
  document_type: string;
  title: string;
  status: 'draft' | 'active' | 'signed' | 'archived';
  client_name?: string;
  property_address?: string;
  generated_by: string;
  signed_by_client: boolean;
  signed_by_agent: boolean;
  created_at: string;
  updated_at: string;
}

const DocumentsList: React.FC = () => {
  const [documents, setDocuments] = useState<GeneratedDocument[]>([]);
  const [filteredDocuments, setFilteredDocuments] = useState<GeneratedDocument[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<GeneratedDocument | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');

  const { isOpen, onOpen, onClose } = useDisclosure();
  const { 
    isOpen: isDeleteOpen, 
    onOpen: onDeleteOpen, 
    onClose: onDeleteClose 
  } = useDisclosure();
  
  const toast = useToast();
  const cancelRef = React.useRef<HTMLButtonElement>(null);

  // Theme colors
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {
    filterDocuments();
  }, [documents, searchTerm, statusFilter, typeFilter]);

  const fetchDocuments = async () => {
    // TODO: Fetch from API
    const mockDocuments: GeneratedDocument[] = [
      {
        id: '1',
        document_number: 'GI-CV-2024-12-0001',
        template_name: 'Contrato de Compra-Venta Estándar',
        document_type: 'sale_contract',
        title: 'Venta Casa Los Rosales',
        status: 'signed',
        client_name: 'Juan Pérez',
        property_address: 'Calle 123 #45-67, Bogotá',
        generated_by: 'María González',
        signed_by_client: true,
        signed_by_agent: true,
        created_at: '2024-12-15T10:30:00Z',
        updated_at: '2024-12-16T14:20:00Z'
      },
      {
        id: '2',
        document_number: 'GI-AL-2024-12-0002',
        template_name: 'Contrato de Arrendamiento Residencial',
        document_type: 'rental_contract',
        title: 'Alquiler Apartamento Centro',
        status: 'active',
        client_name: 'Ana Martínez',
        property_address: 'Carrera 15 #23-45, Medellín',
        generated_by: 'Carlos Rodríguez',
        signed_by_client: true,
        signed_by_agent: false,
        created_at: '2024-12-14T09:15:00Z',
        updated_at: '2024-12-14T09:15:00Z'
      },
      {
        id: '3',
        document_number: 'GI-PR-2024-12-0003',
        template_name: 'Contrato de Préstamo Personal',
        document_type: 'loan_contract',
        title: 'Préstamo Personal María Gómez',
        status: 'draft',
        client_name: 'María Gómez',
        generated_by: 'Luis Silva',
        signed_by_client: false,
        signed_by_agent: false,
        created_at: '2024-12-13T16:45:00Z',
        updated_at: '2024-12-13T16:45:00Z'
      },
      {
        id: '4',
        document_number: 'GI-CV-2024-12-0004',
        template_name: 'Contrato de Compra-Venta Estándar',
        document_type: 'sale_contract',
        title: 'Venta Lote La Sabana',
        status: 'archived',
        client_name: 'Roberto Jiménez',
        property_address: 'Lote 15 Manzana C, La Sabana',
        generated_by: 'Patricia Herrera',
        signed_by_client: true,
        signed_by_agent: true,
        created_at: '2024-11-28T11:20:00Z',
        updated_at: '2024-12-01T08:30:00Z'
      }
    ];
    setDocuments(mockDocuments);
  };

  const filterDocuments = () => {
    let filtered = [...documents];

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(doc => 
        doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.document_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.client_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.property_address?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(doc => doc.status === statusFilter);
    }

    // Filter by type
    if (typeFilter !== 'all') {
      filtered = filtered.filter(doc => doc.document_type === typeFilter);
    }

    setFilteredDocuments(filtered);
  };

  const handleViewDocument = (document: GeneratedDocument) => {
    setSelectedDocument(document);
    onOpen();
  };

  const handleDownloadDocument = (document: GeneratedDocument) => {
    // TODO: Implement download functionality
    toast({
      title: "Descarga iniciada",
      description: `Descargando ${document.document_number}.pdf`,
      status: "info",
      duration: 3000,
      isClosable: true,
    });
  };

  const handleDeleteDocument = async () => {
    try {
      // TODO: Call API to delete document
      toast({
        title: "Documento eliminado",
        description: "El documento se ha eliminado exitosamente",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      onDeleteClose();
      fetchDocuments();
    } catch (error) {
      toast({
        title: "Error",
        description: "No se pudo eliminar el documento",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: 'yellow',
      active: 'blue',
      signed: 'green',
      archived: 'gray'
    };
    return colors[status] || 'gray';
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      draft: 'Borrador',
      active: 'Activo',
      signed: 'Firmado',
      archived: 'Archivado'
    };
    return labels[status] || status;
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

  const getStatusIcon = (status: string) => {
    const icons: Record<string, any> = {
      draft: FiClock,
      active: FiFileText,
      signed: FiCheckCircle,
      archived: FiArchive
    };
    return icons[status] || FiFileText;
  };

  const getStatsData = () => {
    return {
      total: documents.length,
      draft: documents.filter(d => d.status === 'draft').length,
      active: documents.filter(d => d.status === 'active').length,
      signed: documents.filter(d => d.status === 'signed').length,
      archived: documents.filter(d => d.status === 'archived').length
    };
  };

  const stats = getStatsData();

  return (
    <Container maxW="7xl" py={8}>
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
              Documentos Generados
            </Heading>
            <Text color="gray.600" fontSize="sm">
              GENIUS INDUSTRIES - Gestión de documentos legales
            </Text>
          </VStack>
        </Flex>
        <Divider borderColor="black" />
      </Box>

      {/* Stats Cards */}
      <Grid templateColumns={{ base: '1fr', md: 'repeat(5, 1fr)' }} gap={6} mb={8}>
        <Card border="1px solid" borderColor={borderColor}>
          <CardBody>
            <Flex align="center" justify="space-between">
              <Box>
                <Text color="gray.600" fontSize="sm">Total</Text>
                <Text color="black" fontSize="2xl" fontWeight="bold">
                  {stats.total}
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
                <Text color="gray.600" fontSize="sm">Borradores</Text>
                <Text color="black" fontSize="2xl" fontWeight="bold">
                  {stats.draft}
                </Text>
              </Box>
              <Icon as={FiClock} w={8} h={8} color="yellow.500" />
            </Flex>
          </CardBody>
        </Card>
        
        <Card border="1px solid" borderColor={borderColor}>
          <CardBody>
            <Flex align="center" justify="space-between">
              <Box>
                <Text color="gray.600" fontSize="sm">Activos</Text>
                <Text color="black" fontSize="2xl" fontWeight="bold">
                  {stats.active}
                </Text>
              </Box>
              <Icon as={FiFileText} w={8} h={8} color="blue.500" />
            </Flex>
          </CardBody>
        </Card>
        
        <Card border="1px solid" borderColor={borderColor}>
          <CardBody>
            <Flex align="center" justify="space-between">
              <Box>
                <Text color="gray.600" fontSize="sm">Firmados</Text>
                <Text color="black" fontSize="2xl" fontWeight="bold">
                  {stats.signed}
                </Text>
              </Box>
              <Icon as={FiCheckCircle} w={8} h={8} color="green.500" />
            </Flex>
          </CardBody>
        </Card>
        
        <Card border="1px solid" borderColor={borderColor}>
          <CardBody>
            <Flex align="center" justify="space-between">
              <Box>
                <Text color="gray.600" fontSize="sm">Archivados</Text>
                <Text color="black" fontSize="2xl" fontWeight="bold">
                  {stats.archived}
                </Text>
              </Box>
              <Icon as={FiArchive} w={8} h={8} color="gray.500" />
            </Flex>
          </CardBody>
        </Card>
      </Grid>

      {/* Filters */}
      <Card mb={6}>
        <CardBody>
          <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={4}>
            <InputGroup>
              <InputLeftElement pointerEvents="none">
                <Icon as={FiSearch} color="gray.400" />
              </InputLeftElement>
              <Input 
                placeholder="Buscar documentos..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </InputGroup>
            
            <Select 
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">Todos los estados</option>
              <option value="draft">Borradores</option>
              <option value="active">Activos</option>
              <option value="signed">Firmados</option>
              <option value="archived">Archivados</option>
            </Select>
            
            <Select 
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="all">Todos los tipos</option>
              <option value="sale_contract">Compra-Venta</option>
              <option value="rental_contract">Arrendamiento</option>
              <option value="loan_contract">Préstamo</option>
              <option value="intermediation_contract">Intermediación</option>
            </Select>
          </Grid>
        </CardBody>
      </Card>

      {/* Documents Table */}
      <Card>
        <CardBody>
          <Box overflowX="auto">
            <Table variant="simple">
              <Thead>
                <Tr>
                  <Th color="black">Documento</Th>
                  <Th color="black">Cliente/Propiedad</Th>
                  <Th color="black">Tipo</Th>
                  <Th color="black">Estado</Th>
                  <Th color="black">Firmas</Th>
                  <Th color="black">Fecha</Th>
                  <Th color="black">Acciones</Th>
                </Tr>
              </Thead>
              <Tbody>
                {filteredDocuments.map((document) => (
                  <Tr key={document.id}>
                    <Td>
                      <VStack align="start" spacing={0}>
                        <Text fontWeight="semibold" color="black">
                          {document.title}
                        </Text>
                        <Text fontSize="sm" color="gray.600">
                          {document.document_number}
                        </Text>
                      </VStack>
                    </Td>
                    <Td>
                      <VStack align="start" spacing={0}>
                        <Flex align="center">
                          <Icon as={FiUser} w={3} h={3} color="gray.500" mr={1} />
                          <Text fontSize="sm" color="black">
                            {document.client_name || 'N/A'}
                          </Text>
                        </Flex>
                        {document.property_address && (
                          <Flex align="center">
                            <Icon as={FiHome} w={3} h={3} color="gray.500" mr={1} />
                            <Text fontSize="xs" color="gray.600">
                              {document.property_address}
                            </Text>
                          </Flex>
                        )}
                      </VStack>
                    </Td>
                    <Td>
                      <Badge 
                        colorScheme="blue"
                        variant="subtle"
                      >
                        {getDocumentTypeLabel(document.document_type)}
                      </Badge>
                    </Td>
                    <Td>
                      <Flex align="center">
                        <Icon 
                          as={getStatusIcon(document.status)} 
                          w={4} 
                          h={4} 
                          color={`${getStatusColor(document.status)}.500`}
                          mr={2}
                        />
                        <Badge 
                          colorScheme={getStatusColor(document.status)}
                          variant="subtle"
                        >
                          {getStatusLabel(document.status)}
                        </Badge>
                      </Flex>
                    </Td>
                    <Td>
                      <HStack spacing={1}>
                        <Tooltip label={document.signed_by_client ? 'Cliente firmó' : 'Cliente pendiente'}>
                          <Icon 
                            as={document.signed_by_client ? FiCheckCircle : FiXCircle}
                            w={4} 
                            h={4} 
                            color={document.signed_by_client ? 'green.500' : 'red.500'}
                          />
                        </Tooltip>
                        <Tooltip label={document.signed_by_agent ? 'Agente firmó' : 'Agente pendiente'}>
                          <Icon 
                            as={document.signed_by_agent ? FiCheckCircle : FiXCircle}
                            w={4} 
                            h={4} 
                            color={document.signed_by_agent ? 'green.500' : 'red.500'}
                          />
                        </Tooltip>
                      </HStack>
                    </Td>
                    <Td>
                      <VStack align="start" spacing={0}>
                        <Text fontSize="sm" color="black">
                          {new Date(document.created_at).toLocaleDateString()}
                        </Text>
                        <Text fontSize="xs" color="gray.500">
                          por {document.generated_by}
                        </Text>
                      </VStack>
                    </Td>
                    <Td>
                      <HStack spacing={1}>
                        <Tooltip label="Ver documento">
                          <IconButton
                            aria-label="Ver"
                            icon={<Icon as={FiEye} />}
                            size="sm"
                            variant="ghost"
                            color="black"
                            onClick={() => handleViewDocument(document)}
                          />
                        </Tooltip>
                        <Tooltip label="Descargar PDF">
                          <IconButton
                            aria-label="Descargar"
                            icon={<Icon as={FiDownload} />}
                            size="sm"
                            variant="ghost"
                            color="black"
                            onClick={() => handleDownloadDocument(document)}
                          />
                        </Tooltip>
                        <Menu>
                          <MenuButton
                            as={IconButton}
                            aria-label="Más opciones"
                            icon={<Icon as={FiMoreVertical} />}
                            size="sm"
                            variant="ghost"
                            color="black"
                          />
                          <MenuList>
                            <MenuItem icon={<Icon as={FiEdit3} />}>
                              Editar
                            </MenuItem>
                            <MenuItem icon={<Icon as={FiCopy} />}>
                              Duplicar
                            </MenuItem>
                            <MenuItem icon={<Icon as={FiSend} />}>
                              Enviar por email
                            </MenuItem>
                            <MenuItem 
                              icon={<Icon as={FiTrash2} />}
                              color="red.500"
                              onClick={() => {
                                setSelectedDocument(document);
                                onDeleteOpen();
                              }}
                            >
                              Eliminar
                            </MenuItem>
                          </MenuList>
                        </Menu>
                      </HStack>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
          
          {filteredDocuments.length === 0 && (
            <Box textAlign="center" py={8}>
              <Icon as={FiFileText} w={12} h={12} color="gray.400" mb={4} />
              <Text color="gray.600" fontSize="lg" mb={2}>
                No se encontraron documentos
              </Text>
              <Text color="gray.500" fontSize="sm">
                {searchTerm || statusFilter !== 'all' || typeFilter !== 'all' 
                  ? 'Intenta ajustar los filtros de búsqueda'
                  : 'Aún no hay documentos generados'
                }
              </Text>
            </Box>
          )}
        </CardBody>
      </Card>

      {/* View Document Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="6xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader color="black">
            {selectedDocument?.title}
            <Text fontSize="sm" color="gray.600" fontWeight="normal">
              {selectedDocument?.document_number}
            </Text>
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
              {/* Document preview content would go here */}
              <Box textAlign="center" py={8}>
                <Icon as={FiFileText} w={16} h={16} color="gray.400" mb={4} />
                <Text color="gray.600">
                  Vista previa del documento
                </Text>
                <Text fontSize="sm" color="gray.500">
                  {selectedDocument?.template_name}
                </Text>
              </Box>
            </Box>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cerrar
            </Button>
            <Button 
              leftIcon={<Icon as={FiDownload} />}
              bg="black" 
              color="white"
              _hover={{ bg: 'gray.800' }}
              onClick={() => handleDownloadDocument(selectedDocument!)}
            >
              Descargar PDF
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
              Eliminar Documento
            </AlertDialogHeader>
            <AlertDialogBody>
              ¿Estás seguro de que quieres eliminar el documento "{selectedDocument?.title}"? 
              Esta acción no se puede deshacer.
            </AlertDialogBody>
            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onDeleteClose}>
                Cancelar
              </Button>
              <Button colorScheme="red" onClick={handleDeleteDocument} ml={3}>
                Eliminar
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Container>
  );
};

export default DocumentsList; 