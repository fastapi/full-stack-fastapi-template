import { useState } from 'react'
import {
  Box,
  Flex,
  Heading,
  Button,
  Input,
  Select,
  Badge,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Text,
  HStack,
  VStack,
  IconButton,
  FormControl,
  FormLabel,
  FormErrorMessage,
  CloseButton,
  Checkbox,
  useToast
} from '@chakra-ui/react'

// Importar componentes de tabla desde @chakra-ui/table
import {
  Table,
  Thead,
  Tbody,
  Td,
  Th,
  Tr
} from '@chakra-ui/table'

// useToast ya está importado desde @chakra-ui/react
import { FiPlus, FiEdit2, FiTrash2, FiSearch, FiFilter, FiSave } from 'react-icons/fi'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getUsers,
  createUser,
  updateUser,
  deleteUser,
  type User,
  type UserData,
  type UserUpdate,
  type UserFilters
} from '../../client/usersApi'
// Importación de toast eliminada ya que ahora viene de @chakra-ui/react

export const UserManagement = () => {
  const toast = useToast();
  const queryClient = useQueryClient()
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const { open, onOpen, onClose } = useDisclosure()
  const [isEditing, setIsEditing] = useState(false)

  // Form data
  const [formData, setFormData] = useState<UserData>({
    email: '',
    password: '',
    full_name: '',
    role: 'user',
    is_active: true,
    is_superuser: false
  })

  // Filtros
  const [filters, setFilters] = useState<UserFilters>({
    skip: 0,
    limit: 100
  })

  const roles = [
    { value: 'ceo', label: 'CEO' },
    { value: 'manager', label: 'Gerente' },
    { value: 'supervisor', label: 'Supervisor' },
    { value: 'hr', label: 'Recursos Humanos' },
    { value: 'support', label: 'Atención al Cliente' },
    { value: 'agent', label: 'Agente' },
    { value: 'client', label: 'Cliente' },
    { value: 'user', label: 'Usuario' }
  ]

  // Query para obtener usuarios
  const { data: usersResponse, isLoading, error, refetch } = useQuery({
    queryKey: ['users', filters],
    queryFn: () => getUsers(filters),
    staleTime: 30000,
  })

  // Mutación para crear usuario
  const createUserMutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast({
        title: 'Usuario creado',
        description: 'El usuario se ha creado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      onClose()
      resetForm()
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error?.response?.data?.detail || 'Error al crear el usuario',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    },
  })

  // Mutación para actualizar usuario
  const updateUserMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UserUpdate }) =>
      updateUser(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast({
        title: 'Usuario actualizado',
        description: 'El usuario se ha actualizado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      onClose()
      setSelectedUser(null)
      resetForm()
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error?.response?.data?.detail || 'Error al actualizar el usuario',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    },
  })

  // Mutación para eliminar usuario
  const deleteUserMutation = useMutation({
    mutationFn: deleteUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      toast({
        title: 'Usuario eliminado',
        description: 'El usuario se ha eliminado exitosamente',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    },
    onError: (error: any) => {
      toast({
        title: 'Error',
        description: error?.response?.data?.detail || 'Error al eliminar el usuario',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    },
  })

  const users = usersResponse?.data || []

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRole = !roleFilter || user.role === roleFilter
    return matchesSearch && matchesRole
  })

  const resetForm = () => {
    setFormData({
      email: '',
      password: '',
      full_name: '',
      role: 'user',
      is_active: true,
      is_superuser: false
    })
  }

  const getRoleBadgeColor = (role: string) => {
    const colors = {
      ceo: 'red',
      manager: 'purple',
      supervisor: 'blue',
      hr: 'green',
      support: 'orange',
      agent: 'cyan',
      client: 'gray',
      user: 'gray'
    }
    return colors[role as keyof typeof colors] || 'gray'
  }

  const handleEditUser = (user: User) => {
    setSelectedUser(user)
    setFormData({
      email: user.email,
      password: '', // No mostramos la contraseña actual
      full_name: user.full_name,
      role: user.role,
      is_active: user.is_active,
      is_superuser: user.is_superuser
    })
    setIsEditing(true)
    onOpen()
  }

  const handleCreateUser = () => {
    setSelectedUser(null)
    resetForm()
    setIsEditing(false)
    onOpen()
  }

  const handleSaveUser = () => {
    if (isEditing && selectedUser) {
      // Para actualización, omitir password si está vacío
      const updateData: UserUpdate = {
        email: formData.email,
        full_name: formData.full_name,
        role: formData.role,
        is_active: formData.is_active,
        is_superuser: formData.is_superuser
      }
      
      // Solo incluir password si se proporciona
      if (formData.password.trim()) {
        updateData.password = formData.password
      }

      updateUserMutation.mutate({
        id: selectedUser.id,
        data: updateData
      })
    } else {
      createUserMutation.mutate(formData)
    }
  }

  const handleDeleteUser = (userId: string) => {
    if (window.confirm('¿Está seguro de que desea eliminar este usuario? Esta acción no se puede deshacer.')) {
      deleteUserMutation.mutate(userId)
    }
  }

  if (isLoading) {
    return (
      <Box p={6}>
        <Text>Cargando usuarios...</Text>
      </Box>
    )
  }

  if (error) {
    return (
      <Box p={6}>
        <Text color="red.500">Error cargando usuarios</Text>
        <Button onClick={() => refetch()} mt={4}>
          Reintentar
        </Button>
      </Box>
    )
  }

  return (
    <Box p={6}>
      <VStack gap={6} align="stretch">
        {/* Header */}
        <Flex justify="space-between" align="center">
          <Box>
            <Heading size="lg" color="text">
              Gestión de Usuarios
            </Heading>
            <Text color="text.muted" mt={1}>
              Administra usuarios y roles del sistema - {users.length} usuarios registrados
            </Text>
          </Box>
          <Button colorScheme="blue" onClick={handleCreateUser}>
            <FiPlus style={{ marginRight: '8px' }} />
            Nuevo Usuario
          </Button>
        </Flex>

        {/* Filtros */}
        <Box
          bg="bg.surface"
          p={4}
          borderRadius="lg"
          border="1px"
          borderColor="border"
        >
          <HStack gap={4}>
            <Box flex={1}>
              <Field.Root>
                <Field.Label color="text.muted" fontSize="sm">Buscar</Field.Label>
                <Input
                  placeholder="Buscar por nombre o email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </Field.Root>
            </Box>
            <Box minW="200px">
              <Field.Root>
                <Field.Label color="text.muted" fontSize="sm">Rol</Field.Label>
                <Select
                  placeholder="Todos los roles"
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value)}
                >
                  {roles.map(role => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
                </Select>
              </Field.Root>
            </Box>
            <Box pt={6}>
              <Button variant="outline" borderColor="border" color="text" onClick={() => refetch()}>
                <FiFilter style={{ marginRight: '8px' }} />
                Actualizar
              </Button>
            </Box>
          </HStack>
        </Box>

        {/* Tabla de usuarios */}
        <Box
          bg="bg.surface"
          borderRadius="lg"
          overflow="hidden"
          border="1px"
          borderColor="border"
        >
          <Table variant="simple">
            <Thead bg="gray.100">
              <Tr>
                <Th color="gray.600" borderColor="gray.200">Usuario</Th>
                <Th color="gray.600" borderColor="gray.200">Email</Th>
                <Th color="gray.600" borderColor="gray.200">Rol</Th>
                <Th color="gray.600" borderColor="gray.200">Estado</Th>
                <Th color="gray.600" borderColor="gray.200">Fecha Registro</Th>
                <Th color="gray.600" borderColor="gray.200">Acciones</Th>
              </Tr>
            </Thead>
            <Tbody>
              {filteredUsers.map((user) => (
                <Tr key={user.id} _hover={{ bg: 'gray.50' }}>
                  <Td borderColor="gray.200">
                    <VStack align="start" gap={1}>
                      <Text color="gray.900" fontWeight="medium">
                        {user.full_name}
                      </Text>
                      {user.is_superuser && (
                        <Badge colorScheme="red" size="sm">
                          SUPERUSER
                        </Badge>
                      )}
                    </VStack>
                  </Td>
                  <Td borderColor="gray.200">
                    <Text color="gray.900">{user.email}</Text>
                  </Td>
                  <Td borderColor="gray.200">
                    <Badge colorScheme={getRoleBadgeColor(user.role)}>
                      {roles.find(r => r.value === user.role)?.label || user.role}
                    </Badge>
                  </Td>
                  <Td borderColor="gray.200">
                    <Badge colorScheme={user.is_active ? 'green' : 'red'}>
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </Badge>
                  </Td>
                  <Td borderColor="gray.200">
                    <Text color="gray.600" fontSize="sm">
                      {new Date(user.created_at).toLocaleDateString('es-CO')}
                    </Text>
                  </Td>
                  <Td borderColor="gray.200">
                    <HStack gap={2}>
                      <IconButton
                        aria-label="Editar usuario"
                        size="sm"
                        variant="outline"
                        borderColor="gray.200"
                        color="gray.600"
                        onClick={() => handleEditUser(user)}
                        icon={<FiEdit2 />}
                      />
                      <IconButton
                        aria-label="Eliminar usuario"
                        size="sm"
                        variant="outline"
                        borderColor="gray.200"
                        colorScheme="red"
                        onClick={() => handleDeleteUser(user.id)}
                        isLoading={deleteUserMutation.isPending}
                        icon={<FiTrash2 />}
                      />
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>

          {filteredUsers.length === 0 && (
            <Box p={8} textAlign="center">
              <Text color="text.muted">No se encontraron usuarios</Text>
              <Button mt={4} onClick={handleCreateUser} colorScheme="blue">
                Crear primer usuario
              </Button>
            </Box>
          )}
        </Box>
      </VStack>

      {/* Modal para agregar/editar usuario */}
      <Modal isOpen={open} onClose={onClose} size="md">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <Text color="gray.800" fontSize="lg" fontWeight="bold">
              {selectedUser ? 'Editar Usuario' : 'Nuevo Usuario'}
            </Text>
            <ModalCloseButton />
          </ModalHeader>
          <ModalBody pb={6}>
            <VStack spacing={4}>
              <FormControl>
                <FormLabel color="gray.600">Nombre Completo *</FormLabel>
                <Input 
                  placeholder="Ingresa el nombre completo"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                />
              </FormControl>
              
              <FormControl>
                <FormLabel color="gray.600">Email *</FormLabel>
                <Input 
                  type="email" 
                  placeholder="usuario@example.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </FormControl>
              
              <FormControl>
                <FormLabel color="gray.600">
                  Contraseña {isEditing ? '(dejar vacío para mantener actual)' : '*'}
                </FormLabel>
                <Input 
                  type="password" 
                  placeholder={isEditing ? "Nueva contraseña (opcional)" : "Contraseña"}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
              </FormControl>
              
              <FormControl>
                <FormLabel color="gray.600">Rol *</FormLabel>
                <Select 
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                >
                  {roles.map(role => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
                </Select>
              </FormControl>

              <HStack width="100%" justify="space-between">
                <FormControl display="flex" alignItems="center">
                  <Checkbox
                    isChecked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    mr={2}
                  />
                  <FormLabel mb={0} color="gray.600">Usuario activo</FormLabel>
                </FormControl>

                <FormControl display="flex" alignItems="center">
                  <Checkbox
                    isChecked={formData.is_superuser}
                    onChange={(e) => setFormData({ ...formData, is_superuser: e.target.checked })}
                    mr={2}
                  />
                  <FormLabel mb={0} color="gray.600">Superusuario</FormLabel>
                </FormControl>
              </HStack>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="outline" colorScheme="gray" mr={3} onClick={onClose}>
              Cancelar
            </Button>
            <Button 
              colorScheme="blue"
              onClick={handleSaveUser}
              isLoading={createUserMutation.isPending || updateUserMutation.isPending}
              leftIcon={<FiSave />}
              isDisabled={!formData.email || !formData.full_name || (!isEditing && !formData.password)}
            >
              {selectedUser ? 'Guardar Cambios' : 'Crear Usuario'}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  )
}
