import React from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  SimpleGrid,
  Image,
  Badge,
  Button,
  useToast,
  HStack,
  IconButton,
} from '@chakra-ui/react';
import { FaHeart, FaTrash, FaCalendarAlt } from 'react-icons/fa';
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
  images: string[];
  status: 'available' | 'sold' | 'pending';
  type: 'sale' | 'rent';
  bedrooms: number;
  bathrooms: number;
  area: number;
}

export const FavoritesSection: React.FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();

  // Fetch favorite properties
  const { data: favorites, isLoading } = useQuery({
    queryKey: ['favoriteProperties'],
    queryFn: async () => {
      const { data, error } = await nhost.graphql.request(`
        query GetFavoriteProperties {
          favorite_properties {
            property {
              id
              title
              description
              price
              address
              city
              state
              images
              status
              type
              bedrooms
              bathrooms
              area
            }
          }
        }
      `);
      if (error) throw error;
      return data.favorite_properties.map((fav: any) => fav.property);
    },
  });

  // Remove from favorites mutation
  const removeFavorite = useMutation({
    mutationFn: async (propertyId: string) => {
      const { data, error } = await nhost.graphql.request(`
        mutation RemoveFavorite($propertyId: uuid!) {
          delete_favorite_properties(where: {property_id: {_eq: $propertyId}}) {
            affected_rows
          }
        }
      `, {
        propertyId,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['favoriteProperties'] });
      toast({
        title: 'Propiedad eliminada',
        description: 'La propiedad ha sido eliminada de tus favoritos',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
  });

  // Schedule visit mutation
  const scheduleVisit = useMutation({
    mutationFn: async (propertyId: string) => {
      const { data, error } = await nhost.graphql.request(`
        mutation ScheduleVisit($propertyId: uuid!) {
          insert_property_visits_one(object: {
            property_id: $propertyId,
            status: "pending"
          }) {
            id
          }
        }
      `, {
        propertyId,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      toast({
        title: 'Visita programada',
        description: 'Se ha programado tu visita. Te contactaremos pronto.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  if (isLoading) {
    return <Text>Cargando propiedades favoritas...</Text>;
  }

  if (!favorites?.length) {
    return (
      <Box p={6} bg="bg.surface" borderRadius="lg" shadow="base" border="1px" borderColor="border">
        <Text fontSize="lg" color="text.muted" textAlign="center">
          No tienes propiedades en favoritos
        </Text>
      </Box>
    );
  }

  return (
    <Box p={6} bg="bg.surface" borderRadius="lg" shadow="base" border="1px" borderColor="border">
      <VStack spacing={6} align="stretch">
        <Heading size="lg">Propiedades Favoritas</Heading>
        
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
          {favorites.map((property: Property) => (
            <Box
              key={property.id}
              borderWidth="1px"
              borderRadius="lg"
              overflow="hidden"
              position="relative"
            >
              <Image
                src={property.images[0] || '/placeholder-property.jpg'}
                alt={property.title}
                height="200px"
                width="100%"
                objectFit="cover"
              />
              
              <Box p={4}>
                <HStack justify="space-between" mb={2}>
                  <Badge colorScheme={property.status === 'available' ? 'green' : 'red'}>
                    {property.status === 'available' ? 'Disponible' : 'No Disponible'}
                  </Badge>
                  <IconButton
                    aria-label="Eliminar de favoritos"
                    icon={<FaTrash />}
                    size="sm"
                    variant="ghost"
                    colorScheme="red"
                    onClick={() => removeFavorite.mutate(property.id)}
                  />
                </HStack>

                <Heading size="md" mb={2}>{property.title}</Heading>
                <Text color="gray.600" mb={2}>{property.address}</Text>
                <Text fontWeight="bold" mb={2}>{formatCurrency(property.price)}</Text>
                
                <HStack spacing={4} mb={4}>
                  <Text>{property.bedrooms} hab</Text>
                  <Text>{property.bathrooms} baños</Text>
                  <Text>{property.area}m²</Text>
                </HStack>

                <Button
                  leftIcon={<FaCalendarAlt />}
                  colorScheme="black"
                  size="sm"
                  width="full"
                  onClick={() => scheduleVisit.mutate(property.id)}
                  isDisabled={property.status !== 'available'}
                >
                  Programar Visita
                </Button>
              </Box>
            </Box>
          ))}
        </SimpleGrid>
      </VStack>
    </Box>
  );
}; 