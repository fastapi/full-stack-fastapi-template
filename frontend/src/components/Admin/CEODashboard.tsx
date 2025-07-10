import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Button, Flex, Box, Grid, GridItem, Text } from '@chakra-ui/react'
import { FiHome, FiBarChart2, FiUsers, FiTrendingUp, FiSettings } from 'react-icons/fi'
import { RoleDashboard } from '../Common/RoleDashboard'
import { PropertyCRM } from './PropertyCRM'

interface DashboardData {
  status: string
  data: {
    summary: {
      total_users: number
      active_users: number
      total_properties: number
      total_revenue: number
      active_branches: number
      monthly_growth: number
      active_agents: number
    }
    current_user: {
      id: string
      email: string
      full_name: string
      role: string
      is_superuser: boolean
    }
  }
}

const fetchCEODashboard = async (): Promise<DashboardData> => {
  const response = await fetch('http://localhost:8000/api/v1/ceo/dashboard', {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json',
    },
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch dashboard data')
  }
  
  return response.json()
}

export const CEODashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard')
  
  const tabs = [
    { id: 'dashboard', label: 'Dashboard Ejecutivo', icon: FiBarChart2 },
    { id: 'properties', label: 'Propiedades', icon: FiHome },
    { id: 'analytics', label: 'Analytics', icon: FiTrendingUp },
    { id: 'organization', label: 'Organización', icon: FiUsers },
    { id: 'settings', label: 'Configuración', icon: FiSettings }
  ]

  const { data, isLoading, error } = useQuery({
    queryKey: ['ceo-dashboard'],
    queryFn: fetchCEODashboard,
    refetchInterval: 30000, // Actualizar cada 30 segundos
  })

  const renderContent = () => {
    switch (activeTab) {
      case 'properties':
        return <PropertyCRM />
      case 'analytics':
        return (
          <Box bg="bg.surface" p={6} borderRadius="lg" textAlign="center" border="1px" borderColor="border">
            <Text fontSize="lg" color="text.muted">
              Módulo de Analytics Avanzado en desarrollo
            </Text>
          </Box>
        )
      case 'organization':
        return (
          <Box bg="bg.surface" p={6} borderRadius="lg" textAlign="center" border="1px" borderColor="border">
            <Text fontSize="lg" color="text.muted">
              Módulo de Gestión Organizacional en desarrollo
            </Text>
          </Box>
        )
      case 'settings':
        return (
          <Box bg="bg.surface" p={6} borderRadius="lg" textAlign="center" border="1px" borderColor="border">
            <Text fontSize="lg" color="text.muted">
              Módulo de Configuración del Sistema en desarrollo
            </Text>
          </Box>
        )
      default:
        if (isLoading) {
          return (
            <Box display="flex" justifyContent="center" alignItems="center" height="200px">
              <Text color="text.muted">Cargando datos del dashboard...</Text>
            </Box>
          )
        }

        if (error) {
          return (
            <Box display="flex" justifyContent="center" alignItems="center" height="200px">
              <Text color="red.400">Error cargando datos: {(error as Error).message}</Text>
            </Box>
          )
        }

        const summary = data?.data?.summary

        return (
          <>
            <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={6} mb={8}>
              <GridItem>
                <Box bg="bg.surface" borderRadius="lg" shadow="sm" p={6} border="1px" borderColor="border">
                  <Text color="text.muted" fontSize="sm" mb={2}>Ingresos Totales</Text>
                  <Text fontSize="3xl" fontWeight="bold" color="text">
                    ${summary?.total_revenue?.toLocaleString() || '0'}
                  </Text>
                  <Text color="green.400" fontSize="sm" mt={2}>
                    ↑ {summary?.monthly_growth || 0}% (30 días)
                  </Text>
                </Box>
              </GridItem>
              
              <GridItem>
                <Box bg="bg.surface" borderRadius="lg" shadow="sm" p={6} border="1px" borderColor="border">
                  <Text color="text.muted" fontSize="sm" mb={2}>Propiedades Activas</Text>
                  <Text fontSize="3xl" fontWeight="bold" color="text">
                    {summary?.total_properties || 0}
                  </Text>
                  <Text color="green.400" fontSize="sm" mt={2}>↑ 12% (30 días)</Text>
                </Box>
              </GridItem>
              
              <GridItem>
                <Box bg="bg.surface" borderRadius="lg" shadow="sm" p={6} border="1px" borderColor="border">
                  <Text color="text.muted" fontSize="sm" mb={2}>Agentes Activos</Text>
                  <Text fontSize="3xl" fontWeight="bold" color="text">
                    {summary?.active_agents || 0}
                  </Text>
                  <Text color="green.400" fontSize="sm" mt={2}>↑ 5% (30 días)</Text>
                </Box>
              </GridItem>
              
              <GridItem>
                <Box bg="bg.surface" borderRadius="lg" shadow="sm" p={6} border="1px" borderColor="border">
                  <Text color="text.muted" fontSize="sm" mb={2}>Usuarios Totales</Text>
                  <Text fontSize="3xl" fontWeight="bold" color="text">
                    {summary?.total_users || 0}
                  </Text>
                  <Text color="blue.400" fontSize="sm" mt={2}>
                    {summary?.active_users || 0} activos
                  </Text>
                </Box>
              </GridItem>
            </Grid>

            {/* Información del usuario actual */}
            {data?.data?.current_user && (
              <Box bg="bg.muted" borderRadius="lg" p={4} mt={6} border="1px" borderColor="border.muted">
                <Text fontSize="sm" color="text.muted" mb={2}>Usuario actual:</Text>
                <Flex alignItems="center" gap={4}>
                  <Box>
                    <Text fontWeight="semibold" color="text">{data.data.current_user.full_name}</Text>
                    <Text fontSize="sm" color="text.muted">{data.data.current_user.email}</Text>
                  </Box>
                  <Box 
                    bg="green.500" 
                    color="white" 
                    px={2} 
                    py={1} 
                    borderRadius="md" 
                    fontSize="xs"
                    fontWeight="semibold"
                  >
                    {data.data.current_user.role.toUpperCase()}
                  </Box>
                  {data.data.current_user.is_superuser && (
                    <Box 
                      bg="red.500" 
                      color="white" 
                      px={2} 
                      py={1} 
                      borderRadius="md" 
                      fontSize="xs"
                      fontWeight="semibold"
                    >
                      SUPERUSER
                    </Box>
                  )}
                </Flex>
              </Box>
            )}
          </>
        )
    }
  }

  return (
    <RoleDashboard
      title="Dashboard CEO"
      description="Vista general del negocio y control ejecutivo"
    >
      {/* Navigation Tabs */}
      <Flex mb={6} gap={2}>
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            variant={activeTab === tab.id ? 'solid' : 'outline'}
            colorScheme={activeTab === tab.id ? 'blue' : 'gray'}
            size="sm"
            onClick={() => setActiveTab(tab.id)}
          >
            <tab.icon style={{ marginRight: '8px' }} />
            {tab.label}
          </Button>
        ))}
      </Flex>

      {renderContent()}
    </RoleDashboard>
  )
} 