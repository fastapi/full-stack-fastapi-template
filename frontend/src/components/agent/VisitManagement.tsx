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
  useColorModeValue,
} from '@chakra-ui/react';
import { FaEdit, FaTrash, FaEye, FaPlus, FaCalendarAlt } from 'react-icons/fa';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { nhost } from '../../lib/nhost';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

interface Visit {
  id: string;
  property: {
    id: string;
    title: string;
    address: string;
  };
  client: {
    id: string;
    firstName: string;
    lastName: string;
    email: string;
    phone: string;
  };
  scheduledDate: string;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  notes: string;
  createdAt: string;
  updatedAt: string;
}

interface VisitFormData {
  propertyId: string;
  clientId: string;
  scheduledDate: string;
  notes: string;
}

export const VisitManagement: React.FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedVisit, setSelectedVisit] = useState<Visit | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // Fetch visits
  const { data: visits, isLoading } = useQuery({
    queryKey: ['agentVisits'],
    queryFn: async () => {
      const { data, error } = await nhost.graphql.request(`
        query GetAgentVisits {
          visits(where: {agent_id: {_eq: $agentId}}) {
            id
            property {
              id
              title
              address
            }
            client {
              id
              firstName
              lastName
              email
              phone
            }
            scheduled_date
            status
            notes
            created_at
            updated_at
          }
        }
      `);
      if (error) throw error;
      return data.visits;
    },
  });

  // Fetch properties for select
  const { data: properties } = useQuery({
    queryKey: ['agentProperties'],
    queryFn: async () => {
      const { data, error } = await nhost.graphql.request(`
        query GetAgentProperties {
          properties(where: {agent_id: {_eq: $agentId}}) {
            id
            title
            address
          }
        }
      `);
      if (error) throw error;
      return data.properties;
    },
  });

  // Fetch clients for select
  const { data: clients } = useQuery({
    queryKey: ['agentClients'],
    queryFn: async () => {
      const { data, error } = await nhost.graphql.request(`
        query GetAgentClients {
          clients(where: {agent_id: {_eq: $agentId}}) {
            id
            firstName
            lastName
            email
          }
        }
      `);
      if (error) throw error;
      return data.clients;
    },
  });

  // Create/Update visit mutation
  const saveVisit = useMutation({
    mutationFn: async (data: VisitFormData) => {
      const mutation = isEditing
        ? `
          mutation UpdateVisit($id: uuid!, $visit: visits_set_input!) {
            update_visits_by_pk(pk_columns: {id: $id}, _set: $visit) {
              id
            }
          }
        `
        : `
          mutation CreateVisit($visit: visits_insert_input!) {
            insert_visits_one(object: $visit) {
              id
            }
          }
        `;

      const variables = isEditing
        ? { id: selectedVisit?.id, visit: data }
        : { visit: data };

      const { data: response, error } = await nhost.graphql.request(mutation, variables);
      if (error) throw error;
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agentVisits'] });
      toast({
        title: isEditing ? 'Visita actualizada' : 'Visita creada',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onClose();
    },
  });

  // Delete visit mutation
  const deleteVisit = useMutation({
    mutationFn: async (visitId: string) => {
      const { data, error } = await nhost.graphql.request(`
        mutation DeleteVisit($id: uuid!) {
          delete_visits_by_pk(id: $id) {
            id
          }
        }
      `, {
        id: visitId,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agentVisits'] });
      toast({
        title: 'Visita eliminada',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
  });

  const handleEdit = (visit: Visit) => {
    setSelectedVisit(visit);
    setIsEditing(true);
    onOpen();
  };

  const handleCreate = () => {
    setSelectedVisit(null);
    setIsEditing(false);
    onOpen();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'green';
      case 'pending':
        return 'yellow';
      case 'completed':
        return 'blue';
      case 'cancelled':
        return 'red';
      default:
        return 'gray';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'Confirmada';
      case 'pending':
        return 'Pendiente';
      case 'completed':
        return 'Completada';
      case 'cancelled':
        return 'Cancelada';
      default:
        return status;
    }
  };

  if (isLoading) {
    return <Text>Cargando visitas...</Text>;
  }

  return (
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="base" border="1px" borderColor="border">
      <VStack spacing={6} align="stretch">
        <HStack justify="space-between">
          <Heading size="lg">Gestión de Visitas</Heading>
          <Button
            leftIcon={<FaPlus />}
            colorScheme="black"
            onClick={handleCreate}
          >
            Nueva Visita
          </Button>
        </HStack>

        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Propiedad</Th>
              <Th>Cliente</Th>
              <Th>Fecha</Th>
              <Th>Estado</Th>
              <Th>Notas</Th>
              <Th>Acciones</Th>
            </Tr>
          </Thead>
          <Tbody>
            {visits?.map((visit: Visit) => (
              <Tr key={visit.id}>
                <Td>
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="bold">{visit.property.title}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {visit.property.address}
                    </Text>
                  </VStack>
                </Td>
                <Td>
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="bold">
                      {visit.client.firstName} {visit.client.lastName}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {visit.client.email}
                    </Text>
                  </VStack>
                </Td>
                <Td>
                  {format(new Date(visit.scheduledDate), 'PPP', { locale: es })}
                </Td>
                <Td>
                  <Badge colorScheme={getStatusColor(visit.status)}>
                    {getStatusText(visit.status)}
                  </Badge>
                </Td>
                <Td>
                  <Text fontSize="sm" noOfLines={2}>
                    {visit.notes}
                  </Text>
                </Td>
                <Td>
                  <HStack spacing={2}>
                    <IconButton
                      aria-label="Ver detalles"
                      icon={<FaEye />}
                      size="sm"
                      onClick={() => setSelectedVisit(visit)}
                    />
                    <IconButton
                      aria-label="Editar visita"
                      icon={<FaEdit />}
                      size="sm"
                      onClick={() => handleEdit(visit)}
                    />
                    <IconButton
                      aria-label="Eliminar visita"
                      icon={<FaTrash />}
                      size="sm"
                      colorScheme="red"
                      onClick={() => deleteVisit.mutate(visit.id)}
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
              {isEditing ? 'Editar Visita' : 'Nueva Visita'}
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel>Propiedad</FormLabel>
                  <Select
                    defaultValue={selectedVisit?.property.id}
                    placeholder="Seleccionar propiedad"
                  >
                    {properties?.map((property) => (
                      <option key={property.id} value={property.id}>
                        {property.title} - {property.address}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Cliente</FormLabel>
                  <Select
                    defaultValue={selectedVisit?.client.id}
                    placeholder="Seleccionar cliente"
                  >
                    {clients?.map((client) => (
                      <option key={client.id} value={client.id}>
                        {client.firstName} {client.lastName} - {client.email}
                      </option>
                    ))}
                  </Select>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Fecha y Hora</FormLabel>
                  <Input
                    type="datetime-local"
                    defaultValue={selectedVisit?.scheduledDate}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Notas</FormLabel>
                  <Textarea
                    defaultValue={selectedVisit?.notes}
                    placeholder="Notas adicionales"
                  />
                </FormControl>

                <Button
                  colorScheme="black"
                  width="full"
                  onClick={() => {
                    // Implementar lógica de guardado
                    saveVisit.mutate({
                      propertyId: '',
                      clientId: '',
                      scheduledDate: '',
                      notes: '',
                    });
                  }}
                >
                  {isEditing ? 'Actualizar' : 'Crear'} Visita
                </Button>
              </VStack>
            </ModalBody>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
}; 