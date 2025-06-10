import React from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Button,
  useToast,
  FormControl,
  FormLabel,
  Input,
  Select,
  Switch,
  HStack,
  Divider,
} from '@chakra-ui/react';
import { useForm } from 'react-hook-form';
import { useQuery, useMutation } from '@tanstack/react-query';
import { nhost } from '../../lib/nhost';

interface ProfileData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  notificationPreferences: {
    email: boolean;
    sms: boolean;
    push: boolean;
  };
}

export const ProfileSection: React.FC = () => {
  const toast = useToast();
  const { register, handleSubmit, reset, formState: { errors } } = useForm<ProfileData>();

  // Fetch user profile data
  const { data: profile, isLoading } = useQuery({
    queryKey: ['userProfile'],
    queryFn: async () => {
      const { data, error } = await nhost.graphql.request(`
        query GetUserProfile {
          user {
            id
            firstName
            lastName
            email
            phone
            address
            city
            state
            zipCode
            notificationPreferences
          }
        }
      `);
      if (error) throw error;
      return data.user;
    },
  });

  // Update profile mutation
  const updateProfile = useMutation({
    mutationFn: async (data: ProfileData) => {
      const { data: response, error } = await nhost.graphql.request(`
        mutation UpdateUserProfile($profile: user_profile_set_input!) {
          update_user_profile(where: {id: {_eq: $userId}}, _set: $profile) {
            affected_rows
          }
        }
      `, {
        profile: data,
      });
      if (error) throw error;
      return response;
    },
    onSuccess: () => {
      toast({
        title: 'Perfil actualizado',
        description: 'Tu información ha sido actualizada correctamente',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    },
    onError: (error) => {
      toast({
        title: 'Error',
        description: 'No se pudo actualizar tu perfil',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    },
  });

  // Handle form submission
  const onSubmit = (data: ProfileData) => {
    updateProfile.mutate(data);
  };

  // Reset form with profile data when loaded
  React.useEffect(() => {
    if (profile) {
      reset(profile);
    }
  }, [profile, reset]);

  if (isLoading) {
    return <Text>Cargando perfil...</Text>;
  }

  return (
    <Box p={6} bg="white" borderRadius="lg" shadow="base">
      <VStack spacing={6} align="stretch">
        <Heading size="lg">Perfil de Usuario</Heading>
        
        <form onSubmit={handleSubmit(onSubmit)}>
          <VStack spacing={4} align="stretch">
            <HStack spacing={4}>
              <FormControl isInvalid={!!errors.firstName}>
                <FormLabel>Nombre</FormLabel>
                <Input
                  {...register('firstName', { required: 'Este campo es requerido' })}
                />
              </FormControl>
              
              <FormControl isInvalid={!!errors.lastName}>
                <FormLabel>Apellido</FormLabel>
                <Input
                  {...register('lastName', { required: 'Este campo es requerido' })}
                />
              </FormControl>
            </HStack>

            <FormControl isInvalid={!!errors.email}>
              <FormLabel>Email</FormLabel>
              <Input
                type="email"
                {...register('email', {
                  required: 'Este campo es requerido',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Email inválido',
                  },
                })}
              />
            </FormControl>

            <FormControl isInvalid={!!errors.phone}>
              <FormLabel>Teléfono</FormLabel>
              <Input
                type="tel"
                {...register('phone', { required: 'Este campo es requerido' })}
              />
            </FormControl>

            <FormControl isInvalid={!!errors.address}>
              <FormLabel>Dirección</FormLabel>
              <Input
                {...register('address', { required: 'Este campo es requerido' })}
              />
            </FormControl>

            <HStack spacing={4}>
              <FormControl isInvalid={!!errors.city}>
                <FormLabel>Ciudad</FormLabel>
                <Input
                  {...register('city', { required: 'Este campo es requerido' })}
                />
              </FormControl>

              <FormControl isInvalid={!!errors.state}>
                <FormLabel>Estado</FormLabel>
                <Input
                  {...register('state', { required: 'Este campo es requerido' })}
                />
              </FormControl>

              <FormControl isInvalid={!!errors.zipCode}>
                <FormLabel>Código Postal</FormLabel>
                <Input
                  {...register('zipCode', { required: 'Este campo es requerido' })}
                />
              </FormControl>
            </HStack>

            <Divider my={4} />

            <Heading size="md">Preferencias de Notificación</Heading>
            
            <VStack spacing={4} align="stretch">
              <FormControl display="flex" alignItems="center">
                <FormLabel mb="0">Notificaciones por Email</FormLabel>
                <Switch
                  {...register('notificationPreferences.email')}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel mb="0">Notificaciones por SMS</FormLabel>
                <Switch
                  {...register('notificationPreferences.sms')}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center">
                <FormLabel mb="0">Notificaciones Push</FormLabel>
                <Switch
                  {...register('notificationPreferences.push')}
                />
              </FormControl>
            </VStack>

            <Button
              type="submit"
              colorScheme="black"
              isLoading={updateProfile.isPending}
              mt={4}
            >
              Guardar Cambios
            </Button>
          </VStack>
        </form>
      </VStack>
    </Box>
  );
}; 