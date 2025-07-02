import { useState } from 'react'
import { Grid, GridItem, Box, Heading, Badge, Button, HStack, Progress, Text, Flex } from '@chakra-ui/react'
import { FiHome, FiBarChart2, FiUsers, FiCalendar } from 'react-icons/fi'
import { RoleDashboard } from '../Common/RoleDashboard'
import { PropertyCRM } from './PropertyCRM'

export const AgentDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard')

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: FiBarChart2 },
    { id: 'properties', label: 'Mis Propiedades', icon: FiHome },
    { id: 'clients', label: 'Clientes', icon: FiUsers },
    { id: 'appointments', label: 'Citas', icon: FiCalendar }
  ]

  const renderContent = () => {
    switch (activeTab) {
      case 'properties':
        return <PropertyCRM />
      case 'clients':
        return (
          <Box>
            <Heading size="md" mb={4}>Gestión de Clientes</Heading>
            <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
              <Box fontSize="lg" color="gray.600" textAlign="center">
                Módulo de gestión de clientes en desarrollo
              </Box>
            </Box>
          </Box>
        )
      case 'appointments':
        return (
          <Box>
            <Heading size="md" mb={4}>Calendario de Citas</Heading>
            <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
              <Box fontSize="lg" color="gray.600" textAlign="center">
                Sistema de calendario y citas en desarrollo
              </Box>
            </Box>
          </Box>
        )
      default:
        return (
          <>
            <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={8}>
              <GridItem>
                <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
                  <Box fontSize="sm" color="gray.600" mb={2}>Mis Ventas del Mes</Box>
                  <Box fontSize="2xl" fontWeight="bold" color="gray.900">$45,230</Box>
                  <Box fontSize="sm" color="green.500" mt={1}>↑ 18% (30 días)</Box>
                </Box>
              </GridItem>
              <GridItem>
                <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
                  <Box fontSize="sm" color="gray.600" mb={2}>Propiedades Asignadas</Box>
                  <Box fontSize="2xl" fontWeight="bold" color="gray.900">12</Box>
                  <Box fontSize="sm" color="blue.500" mt={1}>3 nuevas esta semana</Box>
                </Box>
              </GridItem>
              <GridItem>
                <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
                  <Box fontSize="sm" color="gray.600" mb={2}>Clientes Activos</Box>
                  <Box fontSize="2xl" fontWeight="bold" color="gray.900">28</Box>
                  <Box fontSize="sm" color="green.500" mt={1}>↑ 5 nuevos</Box>
                </Box>
              </GridItem>
            </Grid>

            <Grid templateColumns="repeat(2, 1fr)" gap={6}>
              <GridItem>
                <Box>
                  <Heading size="md" mb={4}>Próximas Citas</Heading>
                  <Box bg="white" borderRadius="lg" overflow="hidden" border="1px" borderColor="gray.200">
                    <Box p={4} borderBottom="1px" borderColor="gray.200">
                      <Box fontWeight="medium">Visita - Casa en La Calera</Box>
                      <Box fontSize="sm" color="gray.600">Hoy 2:00 PM - María González</Box>
                    </Box>
                    <Box p={4} borderBottom="1px" borderColor="gray.200">
                      <Box fontWeight="medium">Presentación - Apto Zona Rosa</Box>
                      <Box fontSize="sm" color="gray.600">Mañana 10:00 AM - Carlos Ruiz</Box>
                    </Box>
                    <Box p={4}>
                      <Box fontWeight="medium">Negociación - Oficina Centro</Box>
                      <Box fontSize="sm" color="gray.600">Jueves 3:30 PM - Ana López</Box>
                    </Box>
                  </Box>
                </Box>
              </GridItem>
              <GridItem>
                <Box>
                  <Heading size="md" mb={4}>Propiedades Destacadas</Heading>
                  <Box bg="white" borderRadius="lg" overflow="hidden" border="1px" borderColor="gray.200">
                    <Box p={4} borderBottom="1px" borderColor="gray.200">
                      <Box fontWeight="medium">Apartamento Zona Rosa</Box>
                      <Box fontSize="sm" color="gray.600">$850,000,000 - 3 hab, 2 baños</Box>
                      <Box fontSize="xs" color="green.500" mt={1}>5 consultas esta semana</Box>
                    </Box>
                    <Box p={4} borderBottom="1px" borderColor="gray.200">
                      <Box fontWeight="medium">Casa La Calera</Box>
                      <Box fontSize="sm" color="gray.600">$1,200,000,000 - 4 hab, 3 baños</Box>
                      <Box fontSize="xs" color="orange.500" mt={1}>Reservada</Box>
                    </Box>
                    <Box p={4}>
                      <Box fontWeight="medium">Oficina Centro</Box>
                      <Box fontSize="sm" color="gray.600">$450,000,000 - 120m²</Box>
                      <Box fontSize="xs" color="blue.500" mt={1}>2 consultas pendientes</Box>
                    </Box>
                  </Box>
                </Box>
              </GridItem>
            </Grid>
          </>
        )
    }
  }

  return (
    <RoleDashboard
      title="Dashboard de Agente"
      description="Panel de control para agentes inmobiliarios"
    >
      {/* Navigation Tabs */}
      <Flex mb={6} gap={2}>
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            leftIcon={<tab.icon />}
            variant={activeTab === tab.id ? 'solid' : 'outline'}
            colorScheme={activeTab === tab.id ? 'blue' : 'gray'}
            size="sm"
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </Button>
        ))}
      </Flex>

      {renderContent()}
    </RoleDashboard>
  )
} 
