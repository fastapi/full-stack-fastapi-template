import { useState } from 'react'
import {
  Box,
  Flex,
  Heading,
  Button,
  Input,
  Select,
  Table,
  Badge,
  useDisclosure,
  Dialog,
  Portal,
  CloseButton,
  Field,
  Text,
  HStack,
  VStack,
  IconButton
} from '@chakra-ui/react'
import { FiPlus, FiEdit2, FiTrash2, FiSearch, FiFilter } from 'react-icons/fi'

interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_superuser: boolean
  is_active: boolean
  created_at: string
}

export const UserManagement = () => {
  const [users, setUsers] = useState<User[]>([])
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const { open, onOpen, onClose } = useDisclosure()

  const roles = [
    { value: 'ceo', label: 'CEO' },
    { value: 'manager', label: 'Gerente' },
    { value: 'supervisor', label: 'Supervisor' },
    { value: 'hr', label: 'Recursos Humanos' },
    { value: 'support', label: 'Atención al Cliente' },
    { value: 'agent', label: 'Agente' },
    { value: 'client', label: 'Cliente' }
  ]

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRole = !roleFilter || user.role === roleFilter
    return matchesSearch && matchesRole
  })

  const getRoleBadgeColor = (role: string) => {
    const colors = {
      ceo: 'red',
      manager: 'purple',
      supervisor: 'blue',
      hr: 'green',
      support: 'orange',
      agent: 'cyan',
      client: 'gray'
    }
    return colors[role as keyof typeof colors] || 'gray'
  }

  const handleEditUser = (user: User) => {
    setSelectedUser(user)
    onOpen()
  }

  const handleDeleteUser = (userId: string) => {
    // Implementar eliminación
    console.log('Usuario eliminado:', userId)
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
              Administra usuarios y roles del sistema
            </Text>
          </Box>
          <Button colorScheme="blue" onClick={onOpen}>
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
              <Button variant="outline" borderColor="border" color="text">
                <FiFilter style={{ marginRight: '8px' }} />
                Filtrar
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
          <Table.Root variant="simple">
            <Table.Header bg="bg.muted">
              <Table.Row>
                <Table.ColumnHeader color="text.muted" borderColor="border.muted">Usuario</Table.ColumnHeader>
                <Table.ColumnHeader color="text.muted" borderColor="border.muted">Email</Table.ColumnHeader>
                <Table.ColumnHeader color="text.muted" borderColor="border.muted">Rol</Table.ColumnHeader>
                <Table.ColumnHeader color="text.muted" borderColor="border.muted">Estado</Table.ColumnHeader>
                <Table.ColumnHeader color="text.muted" borderColor="border.muted">Fecha Registro</Table.ColumnHeader>
                <Table.ColumnHeader color="text.muted" borderColor="border.muted">Acciones</Table.ColumnHeader>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {filteredUsers.map((user) => (
                <Table.Row key={user.id}>
                  <Table.Cell borderColor="border.muted">
                    <VStack align="start" gap={1}>
                      <Text color="text" fontWeight="medium">
                        {user.full_name}
                      </Text>
                      {user.is_superuser && (
                        <Badge colorScheme="red" size="sm">
                          SUPERUSER
                        </Badge>
                      )}
                    </VStack>
                  </Table.Cell>
                  <Table.Cell borderColor="border.muted">
                    <Text color="text">{user.email}</Text>
                  </Table.Cell>
                  <Table.Cell borderColor="border.muted">
                    <Badge colorScheme={getRoleBadgeColor(user.role)}>
                      {roles.find(r => r.value === user.role)?.label || user.role}
                    </Badge>
                  </Table.Cell>
                  <Table.Cell borderColor="border.muted">
                    <Badge colorScheme={user.is_active ? 'green' : 'red'}>
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </Badge>
                  </Table.Cell>
                  <Table.Cell borderColor="border.muted">
                    <Text color="text.muted" fontSize="sm">
                      {new Date(user.created_at).toLocaleDateString()}
                    </Text>
                  </Table.Cell>
                  <Table.Cell borderColor="border.muted">
                    <HStack gap={2}>
                      <IconButton
                        aria-label="Editar usuario"
                        size="sm"
                        variant="outline"
                        borderColor="border"
                        color="text"
                        onClick={() => handleEditUser(user)}
                      >
                        <FiEdit2 />
                      </IconButton>
                      <IconButton
                        aria-label="Eliminar usuario"
                        size="sm"
                        variant="outline"
                        borderColor="border"
                        color="red.400"
                        onClick={() => handleDeleteUser(user.id)}
                      >
                        <FiTrash2 />
                      </IconButton>
                    </HStack>
                  </Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table.Root>

          {filteredUsers.length === 0 && (
            <Box p={8} textAlign="center">
              <Text color="text.muted">No se encontraron usuarios</Text>
            </Box>
          )}
        </Box>
      </VStack>

      {/* Modal para agregar/editar usuario */}
      <Dialog.Root open={open} onOpenChange={(e) => e.open ? onOpen() : onClose()}>
        <Portal>
          <Dialog.Backdrop />
          <Dialog.Positioner>
            <Dialog.Content bg="bg.surface" border="1px" borderColor="border">
              <Dialog.Header>
                <Dialog.Title color="text">
                  {selectedUser ? 'Editar Usuario' : 'Nuevo Usuario'}
                </Dialog.Title>
                <Dialog.CloseTrigger asChild>
                  <CloseButton color="text" />
                </Dialog.CloseTrigger>
              </Dialog.Header>
              <Dialog.Body>
                <VStack gap={4}>
                  <Field.Root>
                    <Field.Label color="text.muted">Nombre Completo</Field.Label>
                    <Input placeholder="Ingresa el nombre completo" />
                  </Field.Root>
                  <Field.Root>
                    <Field.Label color="text.muted">Email</Field.Label>
                    <Input type="email" placeholder="usuario@example.com" />
                  </Field.Root>
                  <Field.Root>
                    <Field.Label color="text.muted">Rol</Field.Label>
                    <Select placeholder="Selecciona un rol">
                      {roles.map(role => (
                        <option key={role.value} value={role.value}>
                          {role.label}
                        </option>
                      ))}
                    </Select>
                  </Field.Root>
                </VStack>
              </Dialog.Body>
              <Dialog.Footer>
                <Dialog.ActionTrigger asChild>
                  <Button variant="outline" borderColor="border" color="text" mr={3}>
                    Cancelar
                  </Button>
                </Dialog.ActionTrigger>
                <Button colorScheme="blue">
                  {selectedUser ? 'Guardar Cambios' : 'Crear Usuario'}
                </Button>
              </Dialog.Footer>
            </Dialog.Content>
          </Dialog.Positioner>
        </Portal>
      </Dialog.Root>
    </Box>
  )
}
