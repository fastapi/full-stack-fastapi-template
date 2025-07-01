import { 
  Box, 
  Grid, 
  VStack, 
  HStack, 
  Text, 
  Card, 
  CardBody,
  Badge,
  Progress,
  Button,
  SimpleGrid
} from "@chakra-ui/react"
import { useUser } from '@clerk/clerk-react'
import { Link } from "@tanstack/react-router"

interface DashboardProps {
  role?: string
}

export function Dashboard({ role }: DashboardProps) {
  const { user } = useUser()
  const userRole = user?.publicMetadata?.role as string || role || "agent"

  // Datos de ejemplo - reemplazar con datos reales de la API
  const stats = getStatsForRole(userRole)
  const recentActivities = getRecentActivitiesForRole(userRole)
  const quickActions = getQuickActionsForRole(userRole)

  return (
    <Box p={6} bg="bg" minH="100vh">
      {/* Header */}
      <VStack align="start" spacing={4} mb={8}>
        <Text fontSize="3xl" fontWeight="bold" color="text">
          Dashboard {getRoleDisplayName(userRole)}
        </Text>
        <Text color="text.muted">
          Bienvenido, {user?.firstName || user?.emailAddresses[0]?.emailAddress}
        </Text>
      </VStack>

      {/* Stats Grid */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mb={8}>
        {stats.map(( index) => (
          <Card key={index} bg="bg.surface" borderColor="border">
            <CardBody>
              <Box>
                <Text color="text.muted" fontSize="sm">{stat.label}</Text>
                <Text color="text" fontSize="2xl" fontWeight="bold">{stat.value}</Text>
                <HStack color="text.muted" fontSize="sm">
                  <Text color={stat.trend === 'up' ? 'green.500' : 'red.500'}>
                    {stat.trend === 'up' ? '↗' : '↘'}
                  </Text>
                  <Text>{stat.change}</Text>
                </HStack>
              </Box>
            </CardBody>
          </Card>
        ))}
      </SimpleGrid>

      <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={6}>
        {/* Main Content */}
        <VStack spacing={6} align="stretch">
          {/* Progress Section */}
          <Card bg="bg.surface" borderColor="border">
            <CardBody>
              <Text fontSize="lg" fontWeight="semibold" color="text" mb={4}>
                Progreso del Mes
              </Text>
              <VStack spacing={4}>
                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text color="text.muted">Ventas</Text>
                    <Text color="text">75%</Text>
                  </HStack>
                  <Progress value={75} colorScheme="blue" bg="bg.muted" />
                </Box>
                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text color="text.muted">Visitas</Text>
                    <Text color="text">60%</Text>
                  </HStack>
                  <Progress value={60} colorScheme="green" bg="bg.muted" />
                </Box>
                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text color="text.muted">Clientes</Text>
                    <Text color="text">90%</Text>
                  </HStack>
                  <Progress value={90} colorScheme="purple" bg="bg.muted" />
                </Box>
              </VStack>
            </CardBody>
          </Card>

          {/* Recent Activities */}
          <Card bg="bg.surface" borderColor="border">
            <CardBody>
              <Text fontSize="lg" fontWeight="semibold" color="text" mb={4}>
                Actividad Reciente
              </Text>
              <VStack spacing={3} align="stretch">
                {recentActivities.map((activity, index) => (
                  <HStack key={index} p={3} bg="bg.muted" borderRadius="md">
                    <Text fontSize="lg">{activity.icon}</Text>
                    <VStack align="start" spacing={1} flex={1}>
                      <Text color="text" fontWeight="medium">{activity.title}</Text>
                      <Text color="text.muted" fontSize="sm">{activity.description}</Text>
                    </VStack>
                    <Badge colorScheme={activity.status === 'success' ? 'green' : 'blue'}>
                      {activity.time}
                    </Badge>
                  </HStack>
                ))}
              </VStack>
            </CardBody>
          </Card>
        </VStack>

        {/* Sidebar */}
        <VStack spacing={6} align="stretch">
          {/* Quick Actions */}
          <Card bg="bg.surface" borderColor="border">
            <CardBody>
              <Text fontSize="lg" fontWeight="semibold" color="text" mb={4}>
                Acciones Rápidas
              </Text>
              <VStack spacing={3}>
                {quickActions.map((action, index) => (
                  <Link key={index} to={action.path}>
                    <Button
                      variant="outline"
                      borderColor="border"
                      color="text"
                      _hover={{ bg: "bg.muted", borderColor: "blue.500" }}
                      w="full"
                      justifyContent="flex-start"
                      leftIcon={<Text>{action.icon}</Text>}
                    >
                      {action.label}
                    </Button>
                  </Link>
                ))}
              </VStack>
            </CardBody>
          </Card>

          {/* Quick Stats */}
          <Card bg="bg.surface" borderColor="border">
            <CardBody>
              <Text fontSize="lg" fontWeight="semibold" color="text" mb={4}>
                Resumen Rápido
              </Text>
              <VStack spacing={4}>
                <HStack justify="space-between" w="full">
                  <Text color="text.muted">Total Propiedades</Text>
                  <Badge colorScheme="blue">45</Badge>
                </HStack>
                <HStack justify="space-between" w="full">
                  <Text color="text.muted">Clientes Activos</Text>
                  <Badge colorScheme="green">23</Badge>
                </HStack>
                <HStack justify="space-between" w="full">
                  <Text color="text.muted">Visitas Programadas</Text>
                  <Badge colorScheme="orange">12</Badge>
                </HStack>
                <HStack justify="space-between" w="full">
                  <Text color="text.muted">Documentos Pendientes</Text>
                  <Badge colorScheme="red">5</Badge>
                </HStack>
              </VStack>
            </CardBody>
          </Card>
        </VStack>
      </Grid>
    </Box>
  )
}

function getRoleDisplayName(role: string): string {
  const roleNames = {
    ceo: "CEO",
    manager: "Gerente", 
    supervisor: "Supervisor",
    hr: "Recursos Humanos",
    support: "Atención al Cliente",
    agent: "Agente"
  }
  return roleNames[role as keyof typeof roleNames] || "Usuario"
}

function getStatsForRole(role: string) {
  const baseStats = [
    { label: "Ventas del Mes", value: "$45,000", trend: "up", change: "12%" },
    { label: "Propiedades Activas", value: "23", trend: "up", change: "8%" },
    { label: "Clientes Nuevos", value: "12", trend: "up", change: "15%" },
    { label: "Visitas Programadas", value: "8", trend: "down", change: "3%" }
  ]

  // Personalizar stats según el rol
  if (role === "ceo") {
    return [
      { label: "Ingresos Totales", value: "$250,000", trend: "up", change: "18%" },
      { label: "Sucursales", value: "5", trend: "up", change: "25%" },
      { label: "Empleados", value: "45", trend: "up", change: "10%" },
      { label: "ROI", value: "23%", trend: "up", change: "5%" }
    ]
  }

  return baseStats
}

function getRecentActivitiesForRole(role: string) {
  return [
    {
      icon: "🏠",
      title: "Nueva propiedad agregada",
      description: "Casa en zona norte - $120,000",
      time: "2h",
      status: "success"
    },
    {
      icon: "👥",
      title: "Cliente nuevo registrado",
      description: "Juan Pérez - Interesado en apartamentos",
      time: "4h",
      status: "info"
    },
    {
      icon: "📅",
      title: "Visita programada",
      description: "Apartamento centro - Mañana 10:00 AM",
      time: "6h",
      status: "info"
    },
    {
      icon: "📋",
      title: "Documento generado",
      description: "Contrato de venta - Casa zona sur",
      time: "1d",
      status: "success"
    }
  ]
}

function getQuickActionsForRole(role: string) {
  const baseActions = [
    { icon: "➕", label: "Agregar Propiedad", path: "/properties/add" },
    { icon: "👥", label: "Gestionar Clientes", path: "/clients" },
    { icon: "📅", label: "Programar Visita", path: "/visits" },
    { icon: "📋", label: "Generar Documento", path: "/legal/generator" }
  ]

  if (role === "ceo") {
    return [
      { icon: "📊", label: "Ver Reportes", path: "/reports" },
      { icon: "👤", label: "Gestionar Usuarios", path: "/admin/users" },
      { icon: "⚙️", label: "Configuración", path: "/admin/settings" },
      { icon: "💰", label: "Análisis Financiero", path: "/financial" }
    ]
  }

  return baseActions
} 
