 teimport React, { useState } from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Button,
  useToast,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  HStack,
  IconButton,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Flex,
} from '@chakra-ui/react';
import { FaEdit, FaTrash, FaEye, FaPlus, FaPhone, FaEnvelope, FaSave, FaSearch } from 'react-icons/fa';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getClients,
  createClient,
  updateClient,
  deleteClient,
  getClientTypeOptions,
  getClientStatusOptions,
  type Client,
  type ClientData,
  type ClientFilters
} from '../../client/clientsApi';

export const ClientManagement: React.FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // Filtros y búsqueda
  const [filters, setFilters] = useState<ClientFilters>({
    skip: 0,
    limit: 20,
    client_type: '',
    status: '',
    search: ''
  });

  // Form data
  const [formData, setFormData] = useState<ClientData>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    client_type: 'buyer',
    status: 'active',
    notes: ''
  });

  // Fetch clients
  const { data: clientsResponse, isLoading, error, refetch } = useQuery({
    queryKey: ['clients', filters],
    queryFn: () => getClients(filters),
    staleTime: 30000,
  });

  // Fetch client type options
  const { data: typeOptions } = useQuery({
    queryKey: ['clientTypeOptions'],
    queryFn: getClientTypeOptions,
    staleTime: 300000, // Cache por 5 minutos
  });

  // Fetch client status options
  const { data: statusOptions } = useQuery({
    queryKey: ['clientStatusOptions'],
    queryFn: getClientStatusOptions,
    staleTime: 300000,
  });

  // Create client mutation
  const createClientMutation = useMutation({
    mutationFn: createClient,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      toast({
        title: 'Cliente creado',
        description: 'El cliente se ha creado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onClose();
      resetForm();
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error?.response?.data?.detail || 'Error al crear el cliente',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  // Update client mutation
  const updateClientMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ClientData> }) =>
      updateClient(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      toast({
        title: 'Cliente actualizado',
        description: 'El cliente se ha actualizado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onClose();
      setSelectedClient(null);
      resetForm();
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error?.response?.data?.detail || 'Error al actualizar el cliente',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  // Delete client mutation
  const deleteClientMutation = useMutation({
    mutationFn: deleteClient,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      toast({
        title: 'Cliente eliminado',
        description: 'El cliente se ha eliminado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error?.response?.data?.detail || 'Error al eliminar el cliente',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  const clients = clientsResponse?.data || [];
  const totalClients = clientsResponse?.total || 0;

  const resetForm = () => {
    setFormData({
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      client_type: 'buyer',
      status: 'active',
      notes: ''
    });
  };

  const handleEdit = (client: Client) => {
    setSelectedClient(client);
    setFormData({
      first_name: client.first_name,
      last_name: client.last_name,
      email: client.email,
      phone: client.phone || '',
      client_type: client.client_type,
      status: client.status,
      notes: client.notes || ''
    });
    setIsEditing(true);
    onOpen();
  };

  const handleCreate = () => {
    setSelectedClient(null);
    resetForm();
    setIsEditing(false);
    onOpen();
  };

  const handleSave = () => {
    if (isEditing && selectedClient) {
      updateClientMutation.mutate({
        id: selectedClient.id,
        data: formData
      });
    } else {
      createClientMutation.mutate(formData);
    }
  };

  const handleDelete = (clientId: string) => {
    if (window.confirm('¿Está seguro de que desea eliminar este cliente?')) {
      deleteClientMutation.mutate(clientId);
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'buyer':
        return 'blue';
      case 'seller':
        return 'green';
      case 'both':
        return 'purple';
      default:
        return 'gray';
    }
  };

  const getTypeText = (type: string) => {
    switch (type) {
      case 'buyer':
        return 'Comprador';
      case 'seller':
        return 'Vendedor';
      case 'both':
        return 'Ambos';
      default:
        return type;
    }
  };

  if (isLoading) {
    return (
      <Box p={6}>
        <Text>Cargando clientes...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={6}>
        <Text color="red.500">Error cargando clientes</Text>
        <Button onClick={() => refetch()} mt={4}>
          Reintentar
        </Button>
      </Box>
    );
  }

  return (
    <Box p={6} bg="bg.surface" borderRadius="lg" shadow="base" border="1px" borderColor="border">
      {/* Header */}
      <HStack justify="space-between" mb={6}>
        <Box>
          <Heading size="lg">Gestión de Clientes</Heading>
          <Text color="text.muted" mt={1}>
            {totalClients} clientes registrados
          </Text>
        </Box>
        <Button
          leftIcon={<FaPlus />}
          colorScheme="blue"
          onClick={handleCreate}
        >
          Nuevo Cliente
        </Button>
      </HStack>

      {/* Filtros */}
      <Box bg="white" p={4} borderRadius="lg" mb={6} border="1px" borderColor="border">
        <Flex gap={4} wrap="wrap" align="end">
          <Box minW="200px">
            <Text fontSize="sm" fontWeight="500" mb={2}>Buscar</Text>
            <Input
              placeholder="Nombre, apellido o email..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              leftElement={<FaSearch />}
            />
          </Box>
          <Box minW="150px">
            <Text fontSize="sm" fontWeight="500" mb={2}>Tipo</Text>
            <Select
              value={filters.client_type}
              onChange={(e) => setFilters({ ...filters, client_type: e.target.value })}
            >
              <option value="">Todos</option>
              {typeOptions?.data.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
          </Box>
          <Box minW="150px">
            <Text fontSize="sm" fontWeight="500" mb={2}>Estado</Text>
            <Select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            >
              <option value="">Todos</option>
              {statusOptions?.data.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
          </Box>
          <Button colorScheme="blue" onClick={() => refetch()}>
            Filtrar
          </Button>
        </Flex>
      </Box>

      {/* Tabla de clientes */}
      <Box bg="white" borderRadius="lg" overflow="hidden" border="1px" borderColor="border">
        <Table variant="simple">
          <Thead bg="gray.50">
            <Tr>
              <Th>Cliente</Th>
              <Th>Contacto</Th>
              <Th>Tipo</Th>
              <Th>Estado</Th>
              <Th>Última Actualización</Th>
              <Th>Acciones</Th>
            </Tr>
          </Thead>
          <Tbody>
            {clients.map((client: Client) => (
              <Tr key={client.id} _hover={{ bg: 'gray.50' }}>
                <Td>
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="bold">
                      {client.first_name} {client.last_name}
                    </Text>
                    {client.notes && (
                      <Text fontSize="sm" color="gray.600" noOfLines={1}>
                        {client.notes}
                      </Text>
                    )}
                  </VStack>
                </Td>
                <Td>
                  <VStack align="start" spacing={1}>
                    <HStack>
                      <FaEnvelope size={12} />
                      <Text fontSize="sm">{client.email}</Text>
                    </HStack>
                    {client.phone && (
                      <HStack>
                        <FaPhone size={12} />
                        <Text fontSize="sm">{client.phone}</Text>
                      </HStack>
                    )}
                  </VStack>
                </Td>
                <Td>
                  <Badge colorScheme={getTypeColor(client.client_type)}>
                    {getTypeText(client.client_type)}
                  </Badge>
                </Td>
                <Td>
                  <Badge colorScheme={client.status === 'active' ? 'green' : 'red'}>
                    {client.status === 'active' ? 'Activo' : 'Inactivo'}
                  </Badge>
                </Td>
                <Td>{new Date(client.updated_at).toLocaleDateString('es-CO')}</Td>
                <Td>
                  <HStack spacing={2}>
                    <IconButton
                      aria-label="Ver detalles"
                      icon={<FaEye />}
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSelectedClient(client);
                        // Implementar vista de detalles si es necesario
                      }}
                    />
                    <IconButton
                      aria-label="Editar cliente"
                      icon={<FaEdit />}
                      size="sm"
                      colorScheme="blue"
                      variant="outline"
                      onClick={() => handleEdit(client)}
                    />
                    <IconButton
                      aria-label="Eliminar cliente"
                      icon={<FaTrash />}
                      size="sm"
                      colorScheme="red"
                      variant="outline"
                      onClick={() => handleDelete(client.id)}
                      isLoading={deleteClientMutation.isPending}
                    />
                  </HStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>

        {clients.length === 0 && (
          <Box p={8} textAlign="center">
            <Text color="gray.500">No se encontraron clientes</Text>
            <Button mt={4} onClick={handleCreate} colorScheme="blue">
              Crear primer cliente
            </Button>
          </Box>
        )}
      </Box>

      {/* Modal para crear/editar cliente */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            {isEditing ? 'Editar Cliente' : 'Nuevo Cliente'}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={4}>
              <HStack spacing={4} width="100%">
                <FormControl isRequired>
                  <FormLabel>Nombre</FormLabel>
                  <Input
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    placeholder="Nombre"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Apellido</FormLabel>
                  <Input
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    placeholder="Apellido"
                  />
                </FormControl>
              </HStack>

              <FormControl isRequired>
                <FormLabel>Email</FormLabel>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="Email"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Teléfono</FormLabel>
                <Input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="Teléfono"
                />
              </FormControl>

              <HStack spacing={4} width="100%">
                <FormControl isRequired>
                  <FormLabel>Tipo</FormLabel>
                  <Select
                    value={formData.client_type}
                    onChange={(e) => setFormData({ ...formData, client_type: e.target.value as any })}
                  >
                    {typeOptions?.data.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Estado</FormLabel>
                  <Select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                  >
                    {statusOptions?.data.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Select>
                </FormControl>
              </HStack>

              <FormControl>
                <FormLabel>Notas</FormLabel>
                <Textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder="Notas adicionales sobre el cliente..."
                  rows={3}
                />
              </FormControl>

              <HStack spacing={3} width="100%" justify="end" pt={4}>
                <Button variant="outline" onClick={onClose}>
                  Cancelar
                </Button>
                <Button
                  colorScheme="blue"
                  leftIcon={<FaSave />}
                  onClick={handleSave}
                  isLoading={createClientMutation.isPending || updateClientMutation.isPending}
                  isDisabled={!formData.first_name || !formData.last_name || !formData.email}
                >
                  {isEditing ? 'Actualizar' : 'Crear'} Cliente
                </Button>
              </HStack>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
}; 