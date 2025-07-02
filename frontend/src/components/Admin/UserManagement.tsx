import React, { useState, useEffect } from 'react';
import { Box, Flex, Heading, Text, Button } from '@chakra-ui/react';
import { FaEdit, FaTrash, FaPlus, FaLock, FaUnlock } from 'react-icons/fa';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

interface ApiResponse {
  data: User[];
  count: number;
}

export const UserManagement = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch users from API
  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/users/', {
        headers: {
          'Authorization': Bearer ,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data: ApiResponse = await response.json();
        setUsers(data.data);
      } else {
        console.error('Error fetching users:', response.statusText);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const getRoleBadgeColor = (role: string) => {
    const colors: { [key: string]: string } = {
      ceo: '#dc3545',
      manager: '#6f42c1',
      hr: '#20c997',
      agent: '#0d6efd',
      supervisor: '#fd7e14',
      support: '#198754',
    };
    return colors[role.toLowerCase()] || '#6c757d';
  };

  if (loading) {
    return (
      <Box p={6}>
        <Heading size="lg" mb={4}>Gestión de Usuarios</Heading>
        <Text>Cargando usuarios...</Text>
      </Box>
    );
  }

  return (
    <Box p={6}>
      <Flex justify="space-between" align="center" mb={6}>
        <Box>
          <Heading size="lg" color="gray.800">Gestión de Usuarios</Heading>
          <Text color="gray.600" mt={1}>
            Administra usuarios, roles y permisos del sistema
          </Text>
        </Box>
        <Button leftIcon={<FaPlus />} colorScheme="blue" size="lg">
          Agregar Usuario
        </Button>
      </Flex>

      <Box 
        bg="white" 
        borderRadius="lg" 
        overflow="hidden" 
        boxShadow="sm"
        border="1px"
        borderColor="gray.200"
      >
        <Box overflowX="auto">
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ backgroundColor: '#f8f9fa' }}>
              <tr>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 600, color: '#495057' }}>
                  Usuario
                </th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 600, color: '#495057' }}>
                  Rol
                </th>
                <th style={{ padding: '12px', textAlign: 'left', fontWeight: 600, color: '#495057' }}>
                  Estado
                </th>
                <th style={{ padding: '12px', textAlign: 'center', fontWeight: 600, color: '#495057' }}>
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody>
              {users.map((user, index) => (
                <tr 
                  key={user.id} 
                  style={{ 
                    backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa',
                    borderBottom: '1px solid #dee2e6'
                  }}
                >
                  <td style={{ padding: '12px' }}>
                    <Box>
                      <Text fontWeight={600} color="gray.800">{user.full_name}</Text>
                      <Text fontSize="sm" color="gray.500">{user.email}</Text>
                    </Box>
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      backgroundColor: getRoleBadgeColor(user.role),
                      color: 'white',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 600,
                      textTransform: 'uppercase'
                    }}>
                      {user.role}
                    </span>
                    {user.is_superuser && (
                      <span style={{
                        backgroundColor: '#dc3545',
                        color: 'white',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        fontSize: '10px',
                        marginLeft: '4px'
                      }}>
                        SUPER
                      </span>
                    )}
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span style={{
                      backgroundColor: user.is_active ? '#d4edda' : '#f8d7da',
                      color: user.is_active ? '#155724' : '#721c24',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 500
                    }}>
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center' }}>
                    <Flex gap={2} justify="center">
                      <button
                        style={{
                          backgroundColor: '#0d6efd',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          padding: '6px',
                          cursor: 'pointer'
                        }}
                        title="Editar usuario"
                      >
                        <FaEdit size={12} />
                      </button>
                      <button
                        style={{
                          backgroundColor: user.is_active ? '#fd7e14' : '#198754',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          padding: '6px',
                          cursor: 'pointer'
                        }}
                        title={user.is_active ? 'Desactivar usuario' : 'Activar usuario'}
                      >
                        {user.is_active ? <FaLock size={12} /> : <FaUnlock size={12} />}
                      </button>
                      <button
                        style={{
                          backgroundColor: '#dc3545',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          padding: '6px',
                          cursor: 'pointer'
                        }}
                        title="Eliminar usuario"
                      >
                        <FaTrash size={12} />
                      </button>
                    </Flex>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Box>

        {users.length === 0 && (
          <Box p={8} textAlign="center">
            <Text color="gray.500">No hay usuarios disponibles</Text>
          </Box>
        )}
      </Box>
    </Box>
  );
};
