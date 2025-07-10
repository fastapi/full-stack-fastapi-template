import React, { useState } from 'react';
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
} from '@chakra-ui/react';
import { FaEdit, FaTrash, FaEye, FaPlus, FaPhone, FaEnvelope } from 'react-icons/fa';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { nhost } from '../../lib/nhost';

interface Client {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  type: 'buyer' | 'seller' | 'both';
  status: 'active' | 'inactive';
  notes: string;
  createdAt: string;
  updatedAt: string;
  properties: {
    id: string;
    title: string;
    type: 'sale' | 'rent';
    status: string;
  }[];
  visits: {
    id: string;
    property: {
      id: string;
      title: string;
    };
    scheduledDate: string;
    status: string;
  }[];
}

interface ClientFormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  type: 'buyer' | 'seller' | 'both';
  notes: string;
}

export const ClientManagement: React.FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedClient, setSelectedClient] = useState<Client | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // Fetch clients
  const { data: clients, isLoading } = useQuery({
    queryKey: ['agentClients'],
    queryFn: async () => {
      const { data, error } = await nhost.graphql.request(`
        query GetAgentClients {
          clients(where: {agent_id: {_eq: $agentId}}) {
            id
            firstName
            lastName
            email
            phone
            type
            status
            notes
            created_at
            updated_at
            properties {
              id
              title
              type
              status
            }
            visits {
              id
              property {
                id
                title
              }
              scheduled_date
              status
            }
          }
        }
      `);
      if (error) throw error;
      return data.clients;
    },
  });

  // Create/Update client mutation
  const saveClient = useMutation({
    mutationFn: async (data: ClientFormData) => {
      const mutation = isEditing
        ? `
          mutation UpdateClient($id: uuid!, $client: clients_set_input!) {
            update_clients_by_pk(pk_columns: {id: $id}, _set: $client) {
              id
            }
          }
        `
        : `
          mutation CreateClient($client: clients_insert_input!) {
            insert_clients_one(object: $client) {
              id
            }
          }
        `;

      const variables = isEditing
        ? { id: selectedClient?.id, client: data }
        : { client: data };

      const { data: response, error } = await nhost.graphql.request(mutation, variables);
      if (error) throw error;
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agentClients'] });
      toast({
        title: isEditing ? 'Cliente actualizado' : 'Cliente creado',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onClose();
    },
  });

  // Delete client mutation
  const deleteClient = useMutation({
    mutationFn: async (clientId: string) => {
      const { data, error } = await nhost.graphql.request(`
        mutation DeleteClient($id: uuid!) {
          delete_clients_by_pk(id: $id) {
            id
          }
        }
      `, {
        id: clientId,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agentClients'] });
      toast({
        title: 'Cliente eliminado',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
  });

  const handleEdit = (client: Client) => {
    setSelectedClient(client);
    setIsEditing(true);
    onOpen();
  };

  const handleCreate = () => {
    setSelectedClient(null);
    setIsEditing(false);
    onOpen();
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
    return <Text>Cargando clientes...</Text>;
  }

  return (
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="base" border="1px" borderColor="border">
      <VStack spacing={6} align="stretch">
        <HStack justify="space-between">
          <Heading size="lg">Gestión de Clientes</Heading>
          <Button
            leftIcon={<FaPlus />}
            colorScheme="black"
            onClick={handleCreate}
          >
            Nuevo Cliente
          </Button>
        </HStack>

        <Table variant="simple">
          <Thead>
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
            {clients?.map((client: Client) => (
              <Tr key={client.id}>
                <Td>
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="bold">
                      {client.firstName} {client.lastName}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {client.notes}
                    </Text>
                  </VStack>
                </Td>
                <Td>
                  <VStack align="start" spacing={1}>
                    <HStack>
                      <FaEnvelope />
                      <Text fontSize="sm">{client.email}</Text>
                    </HStack>
                    <HStack>
                      <FaPhone />
                      <Text fontSize="sm">{client.phone}</Text>
                    </HStack>
                  </VStack>
                </Td>
                <Td>
                  <Badge colorScheme={getTypeColor(client.type)}>
                    {getTypeText(client.type)}
                  </Badge>
                </Td>
                <Td>
                  <Badge colorScheme={client.status === 'active' ? 'green' : 'red'}>
                    {client.status === 'active' ? 'Activo' : 'Inactivo'}
                  </Badge>
                </Td>
                <Td>{new Date(client.updatedAt).toLocaleDateString()}</Td>
                <Td>
                  <HStack spacing={2}>
                    <IconButton
                      aria-label="Ver detalles"
                      icon={<FaEye />}
                      size="sm"
                      onClick={() => setSelectedClient(client)}
                    />
                    <IconButton
                      aria-label="Editar cliente"
                      icon={<FaEdit />}
                      size="sm"
                      onClick={() => handleEdit(client)}
                    />
                    <IconButton
                      aria-label="Eliminar cliente"
                      icon={<FaTrash />}
                      size="sm"
                      colorScheme="red"
                      onClick={() => deleteClient.mutate(client.id)}
                    />
                  </HStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>

        <Modal isOpen={isOpen} onClose={onClose} size="xl">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>
              {isEditing ? 'Editar Cliente' : 'Nuevo Cliente'}
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
              <Tabs>
                <TabList>
                  <Tab>Información</Tab>
                  {selectedClient && (
                    <>
                      <Tab>Propiedades</Tab>
                      <Tab>Visitas</Tab>
                    </>
                  )}
                </TabList>

                <TabPanels>
                  <TabPanel>
                    <VStack spacing={4}>
                      <HStack spacing={4} width="100%">
                        <FormControl isRequired>
                          <FormLabel>Nombre</FormLabel>
                          <Input
                            defaultValue={selectedClient?.firstName}
                            placeholder="Nombre"
                          />
                        </FormControl>

                        <FormControl isRequired>
                          <FormLabel>Apellido</FormLabel>
                          <Input
                            defaultValue={selectedClient?.lastName}
                            placeholder="Apellido"
                          />
                        </FormControl>
                      </HStack>

                      <FormControl isRequired>
                        <FormLabel>Email</FormLabel>
                        <Input
                          type="email"
                          defaultValue={selectedClient?.email}
                          placeholder="Email"
                        />
                      </FormControl>

                      <FormControl isRequired>
                        <FormLabel>Teléfono</FormLabel>
                        <Input
                          type="tel"
                          defaultValue={selectedClient?.phone}
                          placeholder="Teléfono"
                        />
                      </FormControl>

                      <FormControl isRequired>
                        <FormLabel>Tipo</FormLabel>
                        <Select defaultValue={selectedClient?.type}>
                          <option value="buyer">Comprador</option>
                          <option value="seller">Vendedor</option>
                          <option value="both">Ambos</option>
                        </Select>
                      </FormControl>

                      <FormControl>
                        <FormLabel>Notas</FormLabel>
                        <Textarea
                          defaultValue={selectedClient?.notes}
                          placeholder="Notas adicionales"
                        />
                      </FormControl>

                      <Button
                        colorScheme="black"
                        width="full"
                        onClick={() => {
                          // Implementar lógica de guardado
                          saveClient.mutate({
                            firstName: '',
                            lastName: '',
                            email: '',
                            phone: '',
                            type: 'buyer',
                            notes: '',
                          });
                        }}
                      >
                        {isEditing ? 'Actualizar' : 'Crear'} Cliente
                      </Button>
                    </VStack>
                  </TabPanel>

                  {selectedClient && (
                    <>
                      <TabPanel>
                        <VStack spacing={4} align="stretch">
                          {selectedClient.properties.map((property) => (
                            <Box
                              key={property.id}
                              p={4}
                              borderWidth="1px"
                              borderRadius="md"
                            >
                              <HStack justify="space-between">
                                <VStack align="start" spacing={1}>
                                  <Text fontWeight="bold">{property.title}</Text>
                                  <Badge colorScheme={property.type === 'sale' ? 'blue' : 'purple'}>
                                    {property.type === 'sale' ? 'Venta' : 'Renta'}
                                  </Badge>
                                </VStack>
                                <Badge colorScheme={property.status === 'available' ? 'green' : 'red'}>
                                  {property.status === 'available' ? 'Disponible' : 'No Disponible'}
                                </Badge>
                              </HStack>
                            </Box>
                          ))}
                        </VStack>
                      </TabPanel>

                      <TabPanel>
                        <VStack spacing={4} align="stretch">
                          {selectedClient.visits.map((visit) => (
                            <Box
                              key={visit.id}
                              p={4}
                              borderWidth="1px"
                              borderRadius="md"
                            >
                              <VStack align="start" spacing={1}>
                                <Text fontWeight="bold">{visit.property.title}</Text>
                                <Text fontSize="sm">
                                  Fecha: {new Date(visit.scheduledDate).toLocaleDateString()}
                                </Text>
                                <Badge colorScheme={visit.status === 'confirmed' ? 'green' : 'yellow'}>
                                  {visit.status === 'confirmed' ? 'Confirmada' : 'Pendiente'}
                                </Badge>
                              </VStack>
                            </Box>
                          ))}
                        </VStack>
                      </TabPanel>
                    </>
                  )}
                </TabPanels>
              </Tabs>
            </ModalBody>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
}; 