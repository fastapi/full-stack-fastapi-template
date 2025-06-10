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
  NumberInput,
  NumberInputField,
  Image,
  SimpleGrid,
} from '@chakra-ui/react';
import { FaEdit, FaTrash, FaEye, FaPlus } from 'react-icons/fa';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { nhost } from '../../lib/nhost';
import { formatCurrency } from '../../utils/format';

interface Property {
  id: string;
  title: string;
  description: string;
  price: number;
  address: string;
  city: string;
  state: string;
  type: 'sale' | 'rent';
  status: 'available' | 'pending' | 'sold' | 'rented';
  bedrooms: number;
  bathrooms: number;
  area: number;
  images: string[];
  features: string[];
  createdAt: string;
  updatedAt: string;
}

interface PropertyFormData {
  title: string;
  description: string;
  price: number;
  address: string;
  city: string;
  state: string;
  type: 'sale' | 'rent';
  bedrooms: number;
  bathrooms: number;
  area: number;
  features: string[];
}

export const PropertyManagement: React.FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // Fetch properties
  const { data: properties, isLoading } = useQuery({
    queryKey: ['agentProperties'],
    queryFn: async () => {
      const { data, error } = await nhost.graphql.request(`
        query GetAgentProperties {
          properties(where: {agent_id: {_eq: $agentId}}) {
            id
            title
            description
            price
            address
            city
            state
            type
            status
            bedrooms
            bathrooms
            area
            images
            features
            created_at
            updated_at
          }
        }
      `);
      if (error) throw error;
      return data.properties;
    },
  });

  // Create/Update property mutation
  const saveProperty = useMutation({
    mutationFn: async (data: PropertyFormData) => {
      const mutation = isEditing
        ? `
          mutation UpdateProperty($id: uuid!, $property: properties_set_input!) {
            update_properties_by_pk(pk_columns: {id: $id}, _set: $property) {
              id
            }
          }
        `
        : `
          mutation CreateProperty($property: properties_insert_input!) {
            insert_properties_one(object: $property) {
              id
            }
          }
        `;

      const variables = isEditing
        ? { id: selectedProperty?.id, property: data }
        : { property: data };

      const { data: response, error } = await nhost.graphql.request(mutation, variables);
      if (error) throw error;
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agentProperties'] });
      toast({
        title: isEditing ? 'Propiedad actualizada' : 'Propiedad creada',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onClose();
    },
  });

  // Delete property mutation
  const deleteProperty = useMutation({
    mutationFn: async (propertyId: string) => {
      const { data, error } = await nhost.graphql.request(`
        mutation DeleteProperty($id: uuid!) {
          delete_properties_by_pk(id: $id) {
            id
          }
        }
      `, {
        id: propertyId,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agentProperties'] });
      toast({
        title: 'Propiedad eliminada',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
  });

  const handleEdit = (property: Property) => {
    setSelectedProperty(property);
    setIsEditing(true);
    onOpen();
  };

  const handleCreate = () => {
    setSelectedProperty(null);
    setIsEditing(false);
    onOpen();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'green';
      case 'pending':
        return 'yellow';
      case 'sold':
      case 'rented':
        return 'red';
      default:
        return 'gray';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'available':
        return 'Disponible';
      case 'pending':
        return 'Pendiente';
      case 'sold':
        return 'Vendida';
      case 'rented':
        return 'Rentada';
      default:
        return status;
    }
  };

  if (isLoading) {
    return <Text>Cargando propiedades...</Text>;
  }

  return (
    <Box p={6} bg="white" borderRadius="lg" shadow="base">
      <VStack spacing={6} align="stretch">
        <HStack justify="space-between">
          <Heading size="lg">Gestión de Propiedades</Heading>
          <Button
            leftIcon={<FaPlus />}
            colorScheme="black"
            onClick={handleCreate}
          >
            Nueva Propiedad
          </Button>
        </HStack>

        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Propiedad</Th>
              <Th>Tipo</Th>
              <Th>Precio</Th>
              <Th>Estado</Th>
              <Th>Última Actualización</Th>
              <Th>Acciones</Th>
            </Tr>
          </Thead>
          <Tbody>
            {properties?.map((property: Property) => (
              <Tr key={property.id}>
                <Td>
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="bold">{property.title}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {property.address}
                    </Text>
                  </VStack>
                </Td>
                <Td>
                  <Badge colorScheme={property.type === 'sale' ? 'blue' : 'purple'}>
                    {property.type === 'sale' ? 'Venta' : 'Renta'}
                  </Badge>
                </Td>
                <Td>{formatCurrency(property.price)}</Td>
                <Td>
                  <Badge colorScheme={getStatusColor(property.status)}>
                    {getStatusText(property.status)}
                  </Badge>
                </Td>
                <Td>{new Date(property.updatedAt).toLocaleDateString()}</Td>
                <Td>
                  <HStack spacing={2}>
                    <IconButton
                      aria-label="Ver detalles"
                      icon={<FaEye />}
                      size="sm"
                      onClick={() => window.open(`/properties/${property.id}`, '_blank')}
                    />
                    <IconButton
                      aria-label="Editar propiedad"
                      icon={<FaEdit />}
                      size="sm"
                      onClick={() => handleEdit(property)}
                    />
                    <IconButton
                      aria-label="Eliminar propiedad"
                      icon={<FaTrash />}
                      size="sm"
                      colorScheme="red"
                      onClick={() => deleteProperty.mutate(property.id)}
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
              {isEditing ? 'Editar Propiedad' : 'Nueva Propiedad'}
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel>Título</FormLabel>
                  <Input
                    defaultValue={selectedProperty?.title}
                    placeholder="Título de la propiedad"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Descripción</FormLabel>
                  <Textarea
                    defaultValue={selectedProperty?.description}
                    placeholder="Descripción detallada de la propiedad"
                  />
                </FormControl>

                <HStack spacing={4} width="100%">
                  <FormControl isRequired>
                    <FormLabel>Precio</FormLabel>
                    <NumberInput min={0}>
                      <NumberInputField
                        defaultValue={selectedProperty?.price}
                        placeholder="Precio"
                      />
                    </NumberInput>
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel>Tipo</FormLabel>
                    <Select defaultValue={selectedProperty?.type}>
                      <option value="sale">Venta</option>
                      <option value="rent">Renta</option>
                    </Select>
                  </FormControl>
                </HStack>

                <FormControl isRequired>
                  <FormLabel>Dirección</FormLabel>
                  <Input
                    defaultValue={selectedProperty?.address}
                    placeholder="Dirección completa"
                  />
                </FormControl>

                <HStack spacing={4} width="100%">
                  <FormControl isRequired>
                    <FormLabel>Ciudad</FormLabel>
                    <Input
                      defaultValue={selectedProperty?.city}
                      placeholder="Ciudad"
                    />
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel>Estado</FormLabel>
                    <Input
                      defaultValue={selectedProperty?.state}
                      placeholder="Estado"
                    />
                  </FormControl>
                </HStack>

                <HStack spacing={4} width="100%">
                  <FormControl isRequired>
                    <FormLabel>Habitaciones</FormLabel>
                    <NumberInput min={0}>
                      <NumberInputField
                        defaultValue={selectedProperty?.bedrooms}
                        placeholder="Número de habitaciones"
                      />
                    </NumberInput>
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel>Baños</FormLabel>
                    <NumberInput min={0}>
                      <NumberInputField
                        defaultValue={selectedProperty?.bathrooms}
                        placeholder="Número de baños"
                      />
                    </NumberInput>
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel>Área (m²)</FormLabel>
                    <NumberInput min={0}>
                      <NumberInputField
                        defaultValue={selectedProperty?.area}
                        placeholder="Área en metros cuadrados"
                      />
                    </NumberInput>
                  </FormControl>
                </HStack>

                <Button
                  colorScheme="black"
                  width="full"
                  onClick={() => {
                    // Implementar lógica de guardado
                    saveProperty.mutate({
                      title: '',
                      description: '',
                      price: 0,
                      address: '',
                      city: '',
                      state: '',
                      type: 'sale',
                      bedrooms: 0,
                      bathrooms: 0,
                      area: 0,
                      features: [],
                    });
                  }}
                >
                  {isEditing ? 'Actualizar' : 'Crear'} Propiedad
                </Button>
              </VStack>
            </ModalBody>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
}; 