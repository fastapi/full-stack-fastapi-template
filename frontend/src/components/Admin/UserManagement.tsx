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
  Switch,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import { FaEdit, FaTrash, FaEye, FaPlus, FaLock, FaUnlock } from 'react-icons/fa';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { nhost } from '../../lib/nhost';

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  isActive: boolean;
  createdAt: string;
  lastLogin: string;
  metadata: {
    phone?: string;
    branch?: string;
    department?: string;
  };
}

interface UserFormData {
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  metadata: {
    phone?: string;
    branch?: string;
    department?: string;
  };
}

export const UserManagement: React.FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // Fetch users
  const { data: users, isLoading } = useQuery({
    queryKey: ['adminUsers'],
    queryFn: async () => {
      const { data, error } = await nhost.graphql.request(`
        query GetUsers {
          users {
            id
            email
            firstName
            lastName
            role
            isActive
            created_at
            last_login
            metadata
          }
        }
      `);
      if (error) throw error;
      return data.users;
    },
  });

  // Create/Update user mutation
  const saveUser = useMutation({
    mutationFn: async (data: UserFormData) => {
      const mutation = isEditing
        ? `
          mutation UpdateUser($id: uuid!, $user: users_set_input!) {
            update_users_by_pk(pk_columns: {id: $id}, _set: $user) {
              id
            }
          }
        `
        : `
          mutation CreateUser($user: users_insert_input!) {
            insert_users_one(object: $user) {
              id
            }
          }
        `;

      const variables = isEditing
        ? { id: selectedUser?.id, user: data }
        : { user: data };

      const { data: response, error } = await nhost.graphql.request(mutation, variables);
      if (error) throw error;
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminUsers'] });
      toast({
        title: isEditing ? 'Usuario actualizado' : 'Usuario creado',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      onClose();
    },
  });

  // Toggle user status mutation
  const toggleUserStatus = useMutation({
    mutationFn: async ({ userId, isActive }: { userId: string; isActive: boolean }) => {
      const { data, error } = await nhost.graphql.request(`
        mutation UpdateUserStatus($id: uuid!, $isActive: Boolean!) {
          update_users_by_pk(pk_columns: {id: $id}, _set: {isActive: $isActive}) {
            id
          }
        }
      `, {
        id: userId,
        isActive,
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminUsers'] });
      toast({
        title: 'Estado de usuario actualizado',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
  });

  const handleEdit = (user: User) => {
    setSelectedUser(user);
    setIsEditing(true);
    onOpen();
  };

  const handleCreate = () => {
    setSelectedUser(null);
    setIsEditing(false);
    onOpen();
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'ceo':
        return 'purple';
      case 'manager':
        return 'blue';
      case 'supervisor':
        return 'green';
      case 'agent':
        return 'orange';
      default:
        return 'gray';
    }
  };

  const getRoleText = (role: string) => {
    switch (role) {
      case 'ceo':
        return 'CEO';
      case 'manager':
        return 'Gerente';
      case 'supervisor':
        return 'Supervisor';
      case 'agent':
        return 'Agente';
      default:
        return role;
    }
  };

  if (isLoading) {
    return <Text>Cargando usuarios...</Text>;
  }

  return (
    <Box p={6} bg="white" borderRadius="lg" shadow="base">
      <VStack spacing={6} align="stretch">
        <HStack justify="space-between">
          <Heading size="lg">Gestión de Usuarios</Heading>
          <Button
            leftIcon={<FaPlus />}
            colorScheme="black"
            onClick={handleCreate}
          >
            Nuevo Usuario
          </Button>
        </HStack>

        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Usuario</Th>
              <Th>Rol</Th>
              <Th>Estado</Th>
              <Th>Último Acceso</Th>
              <Th>Acciones</Th>
            </Tr>
          </Thead>
          <Tbody>
            {users?.map((user: User) => (
              <Tr key={user.id}>
                <Td>
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="bold">
                      {user.firstName} {user.lastName}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {user.email}
                    </Text>
                  </VStack>
                </Td>
                <Td>
                  <Badge colorScheme={getRoleColor(user.role)}>
                    {getRoleText(user.role)}
                  </Badge>
                </Td>
                <Td>
                  <Switch
                    isChecked={user.isActive}
                    onChange={() => toggleUserStatus.mutate({
                      userId: user.id,
                      isActive: !user.isActive,
                    })}
                    colorScheme={user.isActive ? 'green' : 'red'}
                  />
                </Td>
                <Td>
                  {user.lastLogin
                    ? new Date(user.lastLogin).toLocaleDateString()
                    : 'Nunca'}
                </Td>
                <Td>
                  <HStack spacing={2}>
                    <IconButton
                      aria-label="Ver detalles"
                      icon={<FaEye />}
                      size="sm"
                      onClick={() => setSelectedUser(user)}
                    />
                    <IconButton
                      aria-label="Editar usuario"
                      icon={<FaEdit />}
                      size="sm"
                      onClick={() => handleEdit(user)}
                    />
                    <IconButton
                      aria-label={user.isActive ? 'Desactivar' : 'Activar'}
                      icon={user.isActive ? <FaLock /> : <FaUnlock />}
                      size="sm"
                      colorScheme={user.isActive ? 'red' : 'green'}
                      onClick={() => toggleUserStatus.mutate({
                        userId: user.id,
                        isActive: !user.isActive,
                      })}
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
              {isEditing ? 'Editar Usuario' : 'Nuevo Usuario'}
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
              <Tabs>
                <TabList>
                  <Tab>Información Básica</Tab>
                  <Tab>Detalles Adicionales</Tab>
                </TabList>

                <TabPanels>
                  <TabPanel>
                    <VStack spacing={4}>
                      <HStack spacing={4} width="100%">
                        <FormControl isRequired>
                          <FormLabel>Nombre</FormLabel>
                          <Input
                            defaultValue={selectedUser?.firstName}
                            placeholder="Nombre"
                          />
                        </FormControl>

                        <FormControl isRequired>
                          <FormLabel>Apellido</FormLabel>
                          <Input
                            defaultValue={selectedUser?.lastName}
                            placeholder="Apellido"
                          />
                        </FormControl>
                      </HStack>

                      <FormControl isRequired>
                        <FormLabel>Email</FormLabel>
                        <Input
                          type="email"
                          defaultValue={selectedUser?.email}
                          placeholder="Email"
                        />
                      </FormControl>

                      <FormControl isRequired>
                        <FormLabel>Rol</FormLabel>
                        <Select defaultValue={selectedUser?.role}>
                          <option value="ceo">CEO</option>
                          <option value="manager">Gerente</option>
                          <option value="supervisor">Supervisor</option>
                          <option value="agent">Agente</option>
                        </Select>
                      </FormControl>
                    </VStack>
                  </TabPanel>

                  <TabPanel>
                    <VStack spacing={4}>
                      <FormControl>
                        <FormLabel>Teléfono</FormLabel>
                        <Input
                          type="tel"
                          defaultValue={selectedUser?.metadata?.phone}
                          placeholder="Teléfono"
                        />
                      </FormControl>

                      <FormControl>
                        <FormLabel>Sucursal</FormLabel>
                        <Input
                          defaultValue={selectedUser?.metadata?.branch}
                          placeholder="Sucursal"
                        />
                      </FormControl>

                      <FormControl>
                        <FormLabel>Departamento</FormLabel>
                        <Input
                          defaultValue={selectedUser?.metadata?.department}
                          placeholder="Departamento"
                        />
                      </FormControl>
                    </VStack>
                  </TabPanel>
                </TabPanels>
              </Tabs>

              <Button
                colorScheme="black"
                width="full"
                mt={6}
                onClick={() => {
                  // Implementar lógica de guardado
                  saveUser.mutate({
                    email: '',
                    firstName: '',
                    lastName: '',
                    role: 'agent',
                    metadata: {},
                  });
                }}
              >
                {isEditing ? 'Actualizar' : 'Crear'} Usuario
              </Button>
            </ModalBody>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
}; 