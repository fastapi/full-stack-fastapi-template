import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useState } from 'react'
import { useAuth, type UserRole } from '@/hooks/useAuth'
import { 
  FiUsers, 
  FiSettings, 
  FiBarChart2, 
  FiHome, 
  FiShield, 
  FiTrendingUp, 
  FiActivity, 
  FiChevronRight, 
  FiEye, 
  FiHeadphones, 
  FiUserCheck, 
  FiPlus 
} from 'react-icons/fi'
import { 
  Box,
  VStack,
  HStack,
  Heading,
  Button,
  Grid,
  Flex,
  Icon,
  Badge,
  Spinner,
  Text
} from '@chakra-ui/react'

// Import existing admin components
import { CEODashboard } from '../components/Admin/CEODashboard'
import { ManagerDashboard } from '../components/Admin/ManagerDashboard'
import { HRDashboard } from '../components/Admin/HRDashboard'
import { AgentDashboard } from '../components/Admin/AgentDashboard'
import { SupervisorDashboard } from '../components/Admin/SupervisorDashboard'
import { SupportDashboard } from '../components/Admin/SupportDashboard'
import { UserManagement } from '../components/Admin/UserManagement'
import { PropertyCRM } from '../components/Admin/PropertyCRM'
import Reports from '../components/Admin/Reports'
import Settings from '../components/Admin/Settings'

function AdminDashboard() {
  const [activeSection, setActiveSection] = useState('overview')

  const systemMetrics = {
    totalUsers: 1247,
    activeProperties: 856,
    totalRevenue: 15420000,
    activeAgents: 45,
    supportTickets: 23,
    systemUptime: '99.9%'
  }

  const quickActions = [
    { icon: FiPlus, label: 'Agregar Usuario', action: () => setActiveSection('users'), colorScheme: 'green' },
    { icon: FiHome, label: 'CRM Propiedades', action: () => setActiveSection('properties'), colorScheme: 'blue' },
    { icon: FiBarChart2, label: 'Reportes', action: () => setActiveSection('reports'), colorScheme: 'purple' },
    { icon: FiSettings, label: 'Configuración', action: () => setActiveSection('settings'), colorScheme: 'gray' }
  ]

  const roleManagement = [
    { role: 'CEO', component: 'ceo', icon: FiShield, description: 'Vista ejecutiva general', users: 1, colorScheme: 'red' },
    { role: 'Manager', component: 'manager', icon: FiUserCheck, description: 'Gestión operativa', users: 8, colorScheme: 'purple' },
    { role: 'HR', component: 'hr', icon: FiUsers, description: 'Recursos humanos', users: 3, colorScheme: 'green' },
    { role: 'Agent', component: 'agent', icon: FiHome, description: 'Agentes inmobiliarios', users: 45, colorScheme: 'orange' },
    { role: 'Supervisor', component: 'supervisor', icon: FiEye, description: 'Supervisión y control', users: 12, colorScheme: 'blue' },
    { role: 'Support', component: 'support', icon: FiHeadphones, description: 'Atención al cliente', users: 15, colorScheme: 'cyan' }
  ]

  const renderContent = () => {
    switch (activeSection) {
      case 'ceo':
        return <CEODashboard />
      case 'manager':
        return <ManagerDashboard />
      case 'hr':
        return <HRDashboard />
      case 'agent':
        return <AgentDashboard />
      case 'supervisor':
        return <SupervisorDashboard />
      case 'support':
        return <SupportDashboard />
      case 'users':
        return <UserManagement />
      case 'properties':
        return <PropertyCRM />
      case 'reports':
        return <Reports />
      case 'settings':
        return <Settings />
      default:
        return (
          <Box p={6}>
            <VStack gap={8} align="stretch">
              {/* Header */}
              <Box>
                <Heading size="2xl" color="text" mb={2}>
                  Panel de Administración GENIUS INDUSTRIES
                </Heading>
                <Text fontSize="lg" color="text.muted" mb={6}>
                  Vista centralizada de todo el sistema inmobiliario
                </Text>
                
                <Box
                  bg="blue.500"
                  color="white"
                  p={4}
                  borderRadius="xl"
                  bgGradient="linear(135deg, blue.400, purple.500)"
                >
                  <HStack gap={4}>
                    <Icon as={FiActivity} boxSize={6} />
                    <Box>
                      <Text fontWeight="600">Sistema Operativo</Text>
                      <Text fontSize="sm" opacity={0.9}>
                        Uptime: {systemMetrics.systemUptime} • Última actualización: hace 2 min
                      </Text>
                    </Box>
                  </HStack>
                </Box>
              </Box>

              {/* Metrics Cards */}
              <Grid templateColumns="repeat(auto-fit, minmax(280px, 1fr))" gap={6}>
                <Box
                  bg="bg.surface"
                  borderRadius="xl"
                  p={6}
                  border="1px"
                  borderColor="border"
                  shadow="md"
                >
                  <Flex justify="space-between" align="center">
                    <Box>
                      <Text color="text.muted" fontSize="sm" mb={1}>Usuarios Totales</Text>
                      <Text fontSize="3xl" fontWeight="700" color="text">
                        {systemMetrics.totalUsers.toLocaleString()}
                      </Text>
                      <Text color="green.400" fontSize="xs" mt={1}>
                        ↑ 12% este mes
                      </Text>
                    </Box>
                    <Box
                      bg="blue.500"
                      borderRadius="xl"
                      p={3}
                      color="white"
                    >
                      <Icon as={FiUsers} boxSize={6} />
                    </Box>
                  </Flex>
                </Box>

                <Box
                  bg="bg.surface"
                  borderRadius="xl"
                  p={6}
                  border="1px"
                  borderColor="border"
                  shadow="md"
                >
                  <Flex justify="space-between" align="center">
                    <Box>
                      <Text color="text.muted" fontSize="sm" mb={1}>Propiedades Activas</Text>
                      <Text fontSize="3xl" fontWeight="700" color="text">
                        {systemMetrics.activeProperties.toLocaleString()}
                      </Text>
                      <Text color="green.400" fontSize="xs" mt={1}>
                        ↑ 8% este mes
                      </Text>
                    </Box>
                    <Box
                      bg="orange.500"
                      borderRadius="xl"
                      p={3}
                      color="white"
                    >
                      <Icon as={FiHome} boxSize={6} />
                    </Box>
                  </Flex>
                </Box>

                <Box
                  bg="bg.surface"
                  borderRadius="xl"
                  p={6}
                  border="1px"
                  borderColor="border"
                  shadow="md"
                >
                  <Flex justify="space-between" align="center">
                    <Box>
                      <Text color="text.muted" fontSize="sm" mb={1}>Ingresos Totales</Text>
                      <Text fontSize="3xl" fontWeight="700" color="text">
                        ${(systemMetrics.totalRevenue / 1000000).toFixed(1)}M
                      </Text>
                      <Text color="green.400" fontSize="xs" mt={1}>
                        ↑ 23% este mes
                      </Text>
                    </Box>
                    <Box
                      bg="cyan.500"
                      borderRadius="xl"
                      p={3}
                      color="white"
                    >
                      <Icon as={FiTrendingUp} boxSize={6} />
                    </Box>
                  </Flex>
                </Box>
              </Grid>

              {/* Quick Actions */}
              <Box>
                <Heading size="lg" color="text" mb={4}>
                  Acciones Rápidas
                </Heading>
                <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={4}>
                  {quickActions.map((action, index) => (
                    <Button
                      key={index}
                      onClick={action.action}
                      variant="outline"
                      borderColor="border"
                      bg="bg.surface"
                      color="text"
                      p={5}
                      h="auto"
                      borderRadius="xl"
                      justifyContent="flex-start"
                      _hover={{
                        bg: "bg.muted",
                        transform: "translateY(-2px)",
                        shadow: "lg"
                      }}
                      transition="all 0.2s"
                    >
                      <HStack gap={3}>
                        <Box
                          bg={`${action.colorScheme}.500`}
                          color="white"
                          borderRadius="lg"
                          p={2}
                        >
                          <Icon as={action.icon} boxSize={4} />
                        </Box>
                        <Text fontWeight="500">{action.label}</Text>
                      </HStack>
                    </Button>
                  ))}
                </Grid>
              </Box>

              {/* Role Management */}
              <Box>
                <Heading size="lg" color="text" mb={4}>
                  Gestión por Roles
                </Heading>
                <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={4}>
                  {roleManagement.map((role, index) => (
                    <Button
                      key={index}
                      onClick={() => setActiveSection(role.component)}
                      variant="outline"
                      borderColor="border"
                      bg="bg.surface"
                      color="text"
                      p={5}
                      h="auto"
                      borderRadius="xl"
                      justifyContent="space-between"
                      _hover={{
                        bg: "bg.muted",
                        transform: "translateY(-2px)",
                        shadow: "lg"
                      }}
                      transition="all 0.2s"
                    >
                      <HStack gap={4}>
                        <Box
                          bg="bg.muted"
                          borderRadius="lg"
                          p={3}
                          color={`${role.colorScheme}.500`}
                        >
                          <Icon as={role.icon} boxSize={6} />
                        </Box>
                        <VStack align="start" gap={1}>
                          <Text fontWeight="600" color="text">
                            {role.role} Dashboard
                          </Text>
                          <Text fontSize="sm" color="text.muted">
                            {role.description}
                          </Text>
                          <Badge colorScheme={role.colorScheme} size="sm">
                            {role.users} usuarios activos
                          </Badge>
                        </VStack>
                      </HStack>
                      <Icon as={FiChevronRight} boxSize={5} color="text.muted" />
                    </Button>
                  ))}
                </Grid>
              </Box>
            </VStack>
          </Box>
        )
    }
  }

  return (
    <Box minHeight="100vh" bg="bg.canvas" p={5}>
      {activeSection !== 'overview' && (
        <Box
          bg="bg.surface"
          borderRadius="xl"
          p={4}
          mb={5}
          border="1px"
          borderColor="border"
          shadow="sm"
        >
          <HStack gap={4}>
            <Button
              onClick={() => setActiveSection('overview')}
              colorScheme="blue"
              size="sm"
            >
              ← Volver al Panel Principal
            </Button>
            <Text color="text.muted">
              {roleManagement.find(r => r.component === activeSection)?.role || 
               (activeSection === 'users' ? 'Gestión de Usuarios' : 
                activeSection === 'properties' ? 'CRM de Propiedades' : '')} Dashboard
            </Text>
          </HStack>
        </Box>
      )}

      <Box
        bg="bg.surface"
        borderRadius="xl"
        border="1px"
        borderColor="border"
        shadow="lg"
        overflow="hidden"
      >
        {renderContent()}
      </Box>
    </Box>
  )
}

// Definir los roles que pueden acceder al panel de administración
const adminRoles: UserRole[] = ['admin', 'ceo', 'manager', 'hr', 'agent', 'supervisor', 'support']

export const Route = createFileRoute('/admin')({
  component: () => {
    const navigate = useNavigate()
    const { isLoaded, isSignedIn, hasRole } = useAuth()
    
    // Si la autenticación está cargando, mostrar spinner
    if (!isLoaded) {
      return (
        <VStack h="100vh" justify="center" align="center">
          <Spinner size="xl" color="blue.500" />
          <Text mt={4} color="gray.600">Cargando panel de administración...</Text>
        </VStack>
      )
    }
    
    // Si el usuario no está autenticado, redirigir al login
    if (!isSignedIn) {
      navigate({ to: '/sign-in' })
      return null
    }
    
    // Verificar si el usuario tiene al menos uno de los roles de administrador
    const hasAdminRole = adminRoles.some(role => hasRole(role))
    if (!hasAdminRole) {
      navigate({ to: '/client-dashboard' })
      return null
    }
    
    // Si el usuario tiene permiso, mostrar el panel de administración
    return <AdminDashboard />
  },
})
