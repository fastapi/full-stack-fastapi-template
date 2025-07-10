import React from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Button,
  useToast,
  HStack,
} from '@chakra-ui/react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { nhost } from '../../lib/nhost';
import { formatDate } from '../../utils/format';

interface Visit {
  id: string;
  property: {
    id: string;
    title: string;
    address: string;
    images: string[];
  };
  scheduledDate: string;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  notes: string;
  agent: {
    id: string;
    firstName: string;
    lastName: string;
    phone: string;
  };
}

export const VisitsSection: React.FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();

  // Fetch scheduled visits
  const { data: visits, isLoading } = useQuery({
    queryKey: ['scheduledVisits'],
    queryFn: async () => {
      const { data, error } = await nhost.graphql.request(`
        query GetScheduledVisits {
          property_visits {
            id
            property {
              id
              title
              address
              images
            }
            scheduled_date
            status
            notes
            agent {
              id
              firstName
              lastName
              phone
            }
          }
        }
      `);
      if (error) throw error;
      return data.property_visits;
    },
  });

  // Cancel visit mutation
  const cancelVisit = useMutation({
    mutationFn: async (visitId: string) => {
      const { data, error } = await nhost.graphql.request(`
        mutation CancelVisit($visitId: uuid!) {
          update_property_visits_by_pk(
            pk_columns: {id: $visitId},
            _set: {status: "cancelled"}
          ) {
            id
          }
        }
      `, {
        visitId,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scheduledVisits'] });
      toast({
        title: 'Visita cancelada',
        description: 'La visita ha sido cancelada correctamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
  });

  // Reschedule visit mutation
  const rescheduleVisit = useMutation({
    mutationFn: async ({ visitId, newDate }: { visitId: string; newDate: string }) => {
      const { data, error } = await nhost.graphql.request(`
        mutation RescheduleVisit($visitId: uuid!, $newDate: timestamptz!) {
          update_property_visits_by_pk(
            pk_columns: {id: $visitId},
            _set: {
              scheduled_date: $newDate,
              status: "pending"
            }
          ) {
            id
          }
        }
      `, {
        visitId,
        newDate,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scheduledVisits'] });
      toast({
        title: 'Visita reprogramada',
        description: 'La visita ha sido reprogramada correctamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
  });

  if (isLoading) {
    return <Text>Cargando visitas programadas...</Text>;
  }

  if (!visits?.length) {
    return (
      <Box p={6} bg="bg.surface" borderRadius="lg" shadow="base" border="1px" borderColor="border">
        <VStack spacing={4}>
          <Heading size="md" color="text">No tienes visitas programadas</Heading>
          <Text color="text.muted">Explora nuestro catálogo y programa una visita</Text>
          <Button colorScheme="blue" as="a" href="/properties">
            Ver Propiedades
          </Button>
        </VStack>
      </Box>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'yellow';
      case 'confirmed':
        return 'blue';
      case 'completed':
        return 'green';
      case 'cancelled':
        return 'red';
      default:
        return 'gray';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'pending':
        return 'Pendiente';
      case 'confirmed':
        return 'Confirmada';
      case 'completed':
        return 'Completada';
      case 'cancelled':
        return 'Cancelada';
      default:
        return status;
    }
  };

  return (
    <Box p={6} bg="bg.surface" borderRadius="lg" shadow="base" border="1px" borderColor="border">
      <VStack spacing={6} align="stretch">
        <Heading size="lg" color="text">Visitas Programadas</Heading>
        
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Propiedad</Th>
              <Th>Fecha</Th>
              <Th>Estado</Th>
              <Th>Agente</Th>
              <Th>Acciones</Th>
            </Tr>
          </Thead>
          <Tbody>
            {visits.map((visit: Visit) => (
              <Tr key={visit.id}>
                <Td>
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="bold">{visit.property.title}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {visit.property.address}
                    </Text>
                  </VStack>
                </Td>
                <Td>{formatDate(visit.scheduledDate)}</Td>
                <Td>
                  <Badge colorScheme={getStatusColor(visit.status)}>
                    {getStatusText(visit.status)}
                  </Badge>
                </Td>
                <Td>
                  <VStack align="start" spacing={1}>
                    <Text>
                      {visit.agent.firstName} {visit.agent.lastName}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {visit.agent.phone}
                    </Text>
                  </VStack>
                </Td>
                <Td>
                  <HStack spacing={2}>
                    {visit.status === 'pending' && (
                      <>
                        <Button
                          size="sm"
                          colorScheme="red"
                          onClick={() => cancelVisit.mutate(visit.id)}
                        >
                          Cancelar
                        </Button>
                        <Button
                          size="sm"
                          colorScheme="blue"
                          onClick={() => {
                            // Implementar lógica de reprogramación
                            const newDate = new Date();
                            newDate.setDate(newDate.getDate() + 1);
                            rescheduleVisit.mutate({
                              visitId: visit.id,
                              newDate: newDate.toISOString(),
                            });
                          }}
                        >
                          Reprogramar
                        </Button>
                      </>
                    )}
                  </HStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      </VStack>
    </Box>
  );
}; 