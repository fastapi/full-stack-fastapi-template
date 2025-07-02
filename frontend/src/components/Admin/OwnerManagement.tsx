import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Input,
  InputGroup,
  InputLeftElement,
  Select,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  IconButton,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Textarea,
  Grid,
  GridItem,
  Card,
  CardBody,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Alert,
  AlertIcon,
  Spinner,
  useToast,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Divider,
} from '@chakra-ui/react';
import {
  FiSearch,
  FiPlus,
  FiEdit,
  FiTrash2,
  FiUser,
  FiUsers,
  FiBuilding,
  FiMail,
  FiPhone,
  FiMapPin,
  FiDollarSign,
  FiMoreVertical,
  FiEye,
  FiDownload,
} from 'react-icons/fi';
import { PropertyOwner, OwnerType } from '../../types/property';

// Mock data para demostración
const mockOwners: PropertyOwner[] = [
  {
    id: '1',
    type: 'own',
    name: 'Genius Industries',
    email: 'propiedades@geniusindustries.org',
    phone: '+57 300 123 4567',
    document_type: 'NIT',
    document_number: '123456789-1',
    company_name: 'Genius Industries S.A.S.',
    created_at: '2024-01-15T00:00:00Z',
    updated_at: '2024-01-15T00:00:00Z',
    active: true,
    notes: 'Propietario principal de la empresa',
  },
  {
    id: '2',
    type: 'third_party',
    name: 'Carlos Rodríguez',
    email: 'carlos.rodriguez@email.com',
    phone: '+57 301 234 5678',
    document_type: 'CC',
    document_number: '1234567890',
    commission_rate: 3.5,
    contact_person: 'Carlos Rodríguez',
    bank_account: {
      bank_name: 'Bancolombia',
      account_type: 'savings',
      account_number: '****1234',
    },
    created_at: '2024-01-20T00:00:00Z',
    updated_at: '2024-01-20T00:00:00Z',
    active: true,
    notes: 'Propietario de 3 apartamentos en El Poblado',
  },
  {
    id: '3',
    type: 'third_party',
    name: 'María González',
    email: 'maria.gonzalez@email.com',
    phone: '+57 302 345 6789',
    document_type: 'CC',
    document_number: '0987654321',
    commission_rate: 4.0,
    contact_person: 'María González',
    created_at: '2024-02-01T00:00:00Z',
    updated_at: '2024-02-01T00:00:00Z',
    active: true,
    notes: 'Propietaria de casa en Laureles',
  },
];

interface OwnerFormData {
  type: OwnerType;
  name: string;
  email: string;
  phone: string;
  document_type: 'CC' | 'CE' | 'NIT' | 'Passport';
  document_number: string;
  company_name?: string;
  contact_person?: string;
  commission_rate?: number;
  bank_name?: string;
  account_type?: 'savings' | 'checking';
  account_number?: string;
  notes?: string;
}

const OwnerManagement: React.FC = () => {
  const [owners, setOwners] = useState<PropertyOwner[]>(mockOwners);
  const [filteredOwners, setFilteredOwners] = useState<PropertyOwner[]>(mockOwners);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [selectedOwner, setSelectedOwner] = useState<PropertyOwner | null>(null);
  const [formMode, setFormMode] = useState<'create' | 'edit'>('create');
  
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  const [formData, setFormData] = useState<OwnerFormData>({
    type: 'third_party',
    name: '',
    email: '',
    phone: '',
    document_type: 'CC',
    document_number: '',
    company_name: '',
    contact_person: '',
    commission_rate: 3.0,
    bank_name: '',
    account_type: 'savings',
    account_number: '',
    notes: '',
  });

  // Filtrar propietarios
  useEffect(() => {
    let filtered = owners;

    // Filtrar por búsqueda
    if (searchTerm) {
      filtered = filtered.filter(owner =>
        owner.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        owner.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        owner.document_number.includes(searchTerm)
      );
    }

    // Filtrar por tipo
    if (filterType !== 'all') {
      filtered = filtered.filter(owner => owner.type === filterType);
    }

    setFilteredOwners(filtered);
  }, [owners, searchTerm, filterType]);

  const handleCreateOwner = () => {
    setFormMode('create');
    setSelectedOwner(null);
    setFormData({
      type: 'third_party',
      name: '',
      email: '',
      phone: '',
      document_type: 'CC',
      document_number: '',
      company_name: '',
      contact_person: '',
      commission_rate: 3.0,
      bank_name: '',
      account_type: 'savings',
      account_number: '',
      notes: '',
    });
    onOpen();
  };

  const handleEditOwner = (owner: PropertyOwner) => {
    setFormMode('edit');
    setSelectedOwner(owner);
    setFormData({
      type: owner.type,
      name: owner.name,
      email: owner.email,
      phone: owner.phone,
      document_type: owner.document_type,
      document_number: owner.document_number,
      company_name: owner.company_name || '',
      contact_person: owner.contact_person || '',
      commission_rate: owner.commission_rate || 3.0,
      bank_name: owner.bank_account?.bank_name || '',
      account_type: owner.bank_account?.account_type || 'savings',
      account_number: owner.bank_account?.account_number || '',
      notes: owner.notes || '',
    });
    onOpen();
  };

  const handleDeleteOwner = async (ownerId: string) => {
    if (window.confirm('¿Está seguro de que desea eliminar este propietario?')) {
      setLoading(true);
      try {
        // Aquí iría la llamada al backend
        setOwners(prev => prev.filter(owner => owner.id !== ownerId));
        toast({
          title: 'Propietario eliminado',
          description: 'El propietario ha sido eliminado exitosamente',
          status: 'success',
          duration: 3000,
        });
      } catch (error) {
        toast({
          title: 'Error',
          description: 'No se pudo eliminar el propietario',
          status: 'error',
          duration: 3000,
        });
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSubmitForm = async () => {
    setLoading(true);
    try {
      const newOwner: PropertyOwner = {
        id: formMode === 'create' ? Date.now().toString() : selectedOwner!.id,
        type: formData.type,
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        document_type: formData.document_type,
        document_number: formData.document_number,
        company_name: formData.company_name || undefined,
        contact_person: formData.contact_person || undefined,
        commission_rate: formData.type === 'third_party' ? formData.commission_rate : undefined,
        bank_account: formData.bank_name ? {
          bank_name: formData.bank_name,
          account_type: formData.account_type!,
          account_number: formData.account_number!,
        } : undefined,
        created_at: formMode === 'create' ? new Date().toISOString() : selectedOwner!.created_at,
        updated_at: new Date().toISOString(),
        active: true,
        notes: formData.notes || undefined,
      };

      if (formMode === 'create') {
        setOwners(prev => [...prev, newOwner]);
        toast({
          title: 'Propietario creado',
          description: 'El propietario ha sido creado exitosamente',
          status: 'success',
          duration: 3000,
        });
      } else {
        setOwners(prev => prev.map(owner => 
          owner.id === selectedOwner!.id ? newOwner : owner
        ));
        toast({
          title: 'Propietario actualizado',
          description: 'El propietario ha sido actualizado exitosamente',
          status: 'success',
          duration: 3000,
        });
      }

      onClose();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo guardar el propietario',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const getOwnerTypeColor = (type: OwnerType) => {
    return type === 'own' ? 'blue' : 'green';
  };

  const getOwnerTypeLabel = (type: OwnerType) => {
    return type === 'own' ? 'Propio' : 'Tercero';
  };

  // Estadísticas
  const stats = {
    total: owners.length,
    own: owners.filter(o => o.type === 'own').length,
    third_party: owners.filter(o => o.type === 'third_party').length,
    average_commission: owners
      .filter(o => o.type === 'third_party' && o.commission_rate)
      .reduce((acc, o) => acc + (o.commission_rate || 0), 0) / 
      owners.filter(o => o.type === 'third_party' && o.commission_rate).length || 0,
  };

  return (
    <Box p={6}>
      {/* Header */}
      <VStack align="stretch" spacing={6}>
        <HStack justify="space-between">
          <VStack align="start" spacing={1}>
            <Text fontSize="2xl" fontWeight="bold" color="gray.800">
              Gestión de Propietarios
            </Text>
            <Text color="gray.600">
              Administra propietarios propios y de terceros
            </Text>
          </VStack>
          <Button
            colorScheme="blue"
            leftIcon={<FiPlus />}
            onClick={handleCreateOwner}
          >
            Nuevo Propietario
          </Button>
        </HStack>

        {/* Estadísticas */}
        <Grid templateColumns="repeat(4, 1fr)" gap={4}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Total Propietarios</StatLabel>
                <StatNumber>{stats.total}</StatNumber>
                <StatHelpText>
                  <FiUsers style={{ display: 'inline', marginRight: '4px' }} />
                  Activos
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
          
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Propios</StatLabel>
                <StatNumber color="blue.500">{stats.own}</StatNumber>
                <StatHelpText>
                  <FiBuilding style={{ display: 'inline', marginRight: '4px' }} />
                  Genius Industries
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Terceros</StatLabel>
                <StatNumber color="green.500">{stats.third_party}</StatNumber>
                <StatHelpText>
                  <FiUser style={{ display: 'inline', marginRight: '4px' }} />
                  Externos
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Comisión Promedio</StatLabel>
                <StatNumber>{stats.average_commission.toFixed(1)}%</StatNumber>
                <StatHelpText>
                  <FiDollarSign style={{ display: 'inline', marginRight: '4px' }} />
                  Terceros
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </Grid>

        {/* Filtros */}
        <HStack spacing={4}>
          <InputGroup maxW="300px">
            <InputLeftElement>
              <FiSearch color="gray.400" />
            </InputLeftElement>
            <Input
              placeholder="Buscar propietarios..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </InputGroup>

          <Select
            maxW="200px"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="all">Todos los tipos</option>
            <option value="own">Propios</option>
            <option value="third_party">Terceros</option>
          </Select>
        </HStack>

        {/* Tabla de propietarios */}
        <Card>
          <CardBody p={0}>
            <Table variant="simple">
              <Thead bg="gray.50">
                <Tr>
                  <Th>Propietario</Th>
                  <Th>Tipo</Th>
                  <Th>Contacto</Th>
                  <Th>Documento</Th>
                  <Th>Comisión</Th>
                  <Th>Estado</Th>
                  <Th>Acciones</Th>
                </Tr>
              </Thead>
              <Tbody>
                {filteredOwners.map((owner) => (
                  <Tr key={owner.id} _hover={{ bg: 'gray.50' }}>
                    <Td>
                      <VStack align="start" spacing={1}>
                        <Text fontWeight="medium">{owner.name}</Text>
                        {owner.company_name && (
                          <Text fontSize="sm" color="gray.600">
                            {owner.company_name}
                          </Text>
                        )}
                      </VStack>
                    </Td>
                    <Td>
                      <Badge
                        colorScheme={getOwnerTypeColor(owner.type)}
                        variant="subtle"
                      >
                        {getOwnerTypeLabel(owner.type)}
                      </Badge>
                    </Td>
                    <Td>
                      <VStack align="start" spacing={1}>
                        <HStack spacing={2}>
                          <FiMail size={14} color="gray.500" />
                          <Text fontSize="sm">{owner.email}</Text>
                        </HStack>
                        <HStack spacing={2}>
                          <FiPhone size={14} color="gray.500" />
                          <Text fontSize="sm">{owner.phone}</Text>
                        </HStack>
                      </VStack>
                    </Td>
                    <Td>
                      <VStack align="start" spacing={1}>
                        <Text fontSize="sm" fontWeight="medium">
                          {owner.document_type}: {owner.document_number}
                        </Text>
                      </VStack>
                    </Td>
                    <Td>
                      {owner.type === 'third_party' && owner.commission_rate ? (
                        <Text fontWeight="medium" color="green.600">
                          {owner.commission_rate}%
                        </Text>
                      ) : (
                        <Text color="gray.400">-</Text>
                      )}
                    </Td>
                    <Td>
                      <Badge
                        colorScheme={owner.active ? 'green' : 'red'}
                        variant="subtle"
                      >
                        {owner.active ? 'Activo' : 'Inactivo'}
                      </Badge>
                    </Td>
                    <Td>
                      <Menu>
                        <MenuButton
                          as={IconButton}
                          icon={<FiMoreVertical />}
                          variant="ghost"
                          size="sm"
                        />
                        <MenuList>
                          <MenuItem
                            icon={<FiEye />}
                            onClick={() => {/* Ver detalles */}}
                          >
                            Ver Detalles
                          </MenuItem>
                          <MenuItem
                            icon={<FiEdit />}
                            onClick={() => handleEditOwner(owner)}
                          >
                            Editar
                          </MenuItem>
                          <MenuItem
                            icon={<FiDownload />}
                            onClick={() => {/* Exportar datos */}}
                          >
                            Exportar
                          </MenuItem>
                          <Divider />
                          <MenuItem
                            icon={<FiTrash2 />}
                            color="red.500"
                            onClick={() => handleDeleteOwner(owner.id)}
                          >
                            Eliminar
                          </MenuItem>
                        </MenuList>
                      </Menu>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>

            {filteredOwners.length === 0 && (
              <Box textAlign="center" py={8}>
                <Text color="gray.500">No se encontraron propietarios</Text>
              </Box>
            )}
          </CardBody>
        </Card>
      </VStack>

      {/* Modal de formulario */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            {formMode === 'create' ? 'Nuevo Propietario' : 'Editar Propietario'}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              {/* Tipo de propietario */}
              <FormControl isRequired>
                <FormLabel>Tipo de Propietario</FormLabel>
                <Select
                  value={formData.type}
                  onChange={(e) => setFormData(prev => ({ 
                    ...prev, 
                    type: e.target.value as OwnerType 
                  }))}
                >
                  <option value="own">Propio (Genius Industries)</option>
                  <option value="third_party">Tercero</option>
                </Select>
              </FormControl>

              {/* Información básica */}
              <Grid templateColumns="repeat(2, 1fr)" gap={4} w="full">
                <FormControl isRequired>
                  <FormLabel>Nombre</FormLabel>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      name: e.target.value 
                    }))}
                    placeholder="Nombre completo"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Email</FormLabel>
                  <Input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      email: e.target.value 
                    }))}
                    placeholder="email@ejemplo.com"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Teléfono</FormLabel>
                  <Input
                    value={formData.phone}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      phone: e.target.value 
                    }))}
                    placeholder="+57 300 123 4567"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Tipo de Documento</FormLabel>
                  <Select
                    value={formData.document_type}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      document_type: e.target.value as any
                    }))}
                  >
                    <option value="CC">Cédula de Ciudadanía</option>
                    <option value="CE">Cédula de Extranjería</option>
                    <option value="NIT">NIT</option>
                    <option value="Passport">Pasaporte</option>
                  </Select>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Número de Documento</FormLabel>
                  <Input
                    value={formData.document_number}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      document_number: e.target.value 
                    }))}
                    placeholder="123456789"
                  />
                </FormControl>

                {formData.type === 'own' && (
                  <FormControl>
                    <FormLabel>Empresa</FormLabel>
                    <Input
                      value={formData.company_name}
                      onChange={(e) => setFormData(prev => ({ 
                        ...prev, 
                        company_name: e.target.value 
                      }))}
                      placeholder="Nombre de la empresa"
                    />
                  </FormControl>
                )}
              </Grid>

              {/* Información específica para terceros */}
              {formData.type === 'third_party' && (
                <>
                  <Grid templateColumns="repeat(2, 1fr)" gap={4} w="full">
                    <FormControl>
                      <FormLabel>Persona de Contacto</FormLabel>
                      <Input
                        value={formData.contact_person}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          contact_person: e.target.value 
                        }))}
                        placeholder="Persona de contacto"
                      />
                    </FormControl>

                    <FormControl>
                      <FormLabel>Tasa de Comisión (%)</FormLabel>
                      <Input
                        type="number"
                        step="0.1"
                        min="0"
                        max="10"
                        value={formData.commission_rate}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          commission_rate: parseFloat(e.target.value) || 0
                        }))}
                      />
                    </FormControl>
                  </Grid>

                  {/* Información bancaria */}
                  <Text fontWeight="medium" alignSelf="start">
                    Información Bancaria (Opcional)
                  </Text>
                  <Grid templateColumns="repeat(3, 1fr)" gap={4} w="full">
                    <FormControl>
                      <FormLabel>Banco</FormLabel>
                      <Input
                        value={formData.bank_name}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          bank_name: e.target.value 
                        }))}
                        placeholder="Nombre del banco"
                      />
                    </FormControl>

                    <FormControl>
                      <FormLabel>Tipo de Cuenta</FormLabel>
                      <Select
                        value={formData.account_type}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          account_type: e.target.value as any
                        }))}
                      >
                        <option value="savings">Ahorros</option>
                        <option value="checking">Corriente</option>
                      </Select>
                    </FormControl>

                    <FormControl>
                      <FormLabel>Número de Cuenta</FormLabel>
                      <Input
                        value={formData.account_number}
                        onChange={(e) => setFormData(prev => ({ 
                          ...prev, 
                          account_number: e.target.value 
                        }))}
                        placeholder="Número de cuenta"
                      />
                    </FormControl>
                  </Grid>
                </>
              )}

              {/* Notas */}
              <FormControl>
                <FormLabel>Notas</FormLabel>
                <Textarea
                  value={formData.notes}
                  onChange={(e) => setFormData(prev => ({ 
                    ...prev, 
                    notes: e.target.value 
                  }))}
                  placeholder="Notas adicionales..."
                  resize="vertical"
                  minH="80px"
                />
              </FormControl>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancelar
            </Button>
            <Button
              colorScheme="blue"
              onClick={handleSubmitForm}
              isLoading={loading}
              loadingText="Guardando..."
            >
              {formMode === 'create' ? 'Crear' : 'Actualizar'}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default OwnerManagement; 
