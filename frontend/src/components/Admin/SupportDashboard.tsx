import { useState } from 'react'
import { Grid, GridItem, Box, Heading, Button, Flex, Badge } from '@chakra-ui/react'
import { FiHome, FiBarChart2, FiMessageSquare, FiPhone, FiHeadphones } from 'react-icons/fi'
import { RoleDashboard } from '../Common/RoleDashboard'
import { PropertyCRM } from './PropertyCRM'

export const SupportDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard')

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: FiBarChart2 },
    { id: 'properties', label: 'Propiedades', icon: FiHome },
    { id: 'tickets', label: 'Tickets', icon: FiMessageSquare },
    { id: 'calls', label: 'Llamadas', icon: FiPhone },
    { id: 'support', label: 'Soporte Técnico', icon: FiHeadphones }
  ]

  const renderContent = () => {
    switch (activeTab) {
      case 'properties':
        return <PropertyCRM />
      case 'tickets':
        return (
          <Box>
            <Heading size="md" mb={4}>Sistema de Tickets</Heading>
            <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
              <Box fontSize="lg" color="gray.600" textAlign="center">
                Sistema de tickets de soporte en desarrollo
              </Box>
            </Box>
          </Box>
        )
      case 'calls':
        return (
          <Box>
            <Heading size="md" mb={4}>Registro de Llamadas</Heading>
            <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
              <Box fontSize="lg" color="gray.600" textAlign="center">
                Sistema de registro de llamadas en desarrollo
              </Box>
            </Box>
          </Box>
        )
      default:
        return (
          <>
            <Grid templateColumns="repeat(4, 1fr)" gap={6} mb={8}>
              <GridItem>
                <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
                  <Box fontSize="sm" color="gray.600" mb={2}>Tickets Abiertos</Box>
                  <Box fontSize="2xl" fontWeight="bold" color="gray.900">23</Box>
                  <Box fontSize="sm" color="red.500" mt={1}>5 urgentes</Box>
                </Box>
              </GridItem>
              <GridItem>
                <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
                  <Box fontSize="sm" color="gray.600" mb={2}>Consultas Hoy</Box>
                  <Box fontSize="2xl" fontWeight="bold" color="gray.900">47</Box>
                  <Box fontSize="sm" color="blue.500" mt={1}>12 sobre propiedades</Box>
                </Box>
              </GridItem>
              <GridItem>
                <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
                  <Box fontSize="sm" color="gray.600" mb={2}>Tiempo Resp. Prom.</Box>
                  <Box fontSize="2xl" fontWeight="bold" color="gray.900">8.5min</Box>
                  <Box fontSize="sm" color="green.500" mt={1}>↓ 2min mejora</Box>
                </Box>
              </GridItem>
              <GridItem>
                <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
                  <Box fontSize="sm" color="gray.600" mb={2}>Satisfacción</Box>
                  <Box fontSize="2xl" fontWeight="bold" color="gray.900">94%</Box>
                  <Box fontSize="sm" color="green.500" mt={1}>↑ 3% este mes</Box>
                </Box>
              </GridItem>
            </Grid>

            <Grid templateColumns="repeat(2, 1fr)" gap={6}>
              <GridItem>
                <Box>
                  <Heading size="md" mb={4}>Tickets Recientes</Heading>
                  <Box bg="white" borderRadius="lg" overflow="hidden" border="1px" borderColor="gray.200">
                    <Box p={4} borderBottom="1px" borderColor="gray.200">
                      <Flex justify="space-between" align="center">
                        <Box>
                          <Box fontWeight="medium">Consulta sobre financiación</Box>
                          <Box fontSize="sm" color="gray.600">Cliente: María González</Box>
                        </Box>
                        <Badge colorScheme="orange">Alta</Badge>
                      </Flex>
                    </Box>
                    <Box p={4} borderBottom="1px" borderColor="gray.200">
                      <Flex justify="space-between" align="center">
                        <Box>
                          <Box fontWeight="medium">Info. apartamento Zona Rosa</Box>
                          <Box fontSize="sm" color="gray.600">Cliente: Carlos Ruiz</Box>
                        </Box>
                        <Badge colorScheme="blue">Media</Badge>
                      </Flex>
                    </Box>
                    <Box p={4} borderBottom="1px" borderColor="gray.200">
                      <Flex justify="space-between" align="center">
                        <Box>
                          <Box fontWeight="medium">Problema con cita</Box>
                          <Box fontSize="sm" color="gray.600">Cliente: Ana López</Box>
                        </Box>
                        <Badge colorScheme="red">Urgente</Badge>
                      </Flex>
                    </Box>
                    <Box p={4}>
                      <Flex justify="space-between" align="center">
                        <Box>
                          <Box fontWeight="medium">Documentación legal</Box>
                          <Box fontSize="sm" color="gray.600">Cliente: Luis Mendoza</Box>
                        </Box>
                        <Badge colorScheme="green">Baja</Badge>
                      </Flex>
                    </Box>
                  </Box>
                </Box>
              </GridItem>
              <GridItem>
                <Box>
                  <Heading size="md" mb={4}>Actividad del Día</Heading>
                  <Box bg="white" borderRadius="lg" overflow="hidden" border="1px" borderColor="gray.200">
                    <Box p={4} borderBottom="1px" borderColor="gray.200">
                      <Box fontSize="xs" color="gray.500">09:30 AM</Box>
                      <Box fontWeight="medium">Llamada entrante - Consulta general</Box>
                      <Box fontSize="sm" color="gray.600">Duración: 12 min</Box>
                    </Box>
                    <Box p={4} borderBottom="1px" borderColor="gray.200">
                      <Box fontSize="xs" color="gray.500">10:15 AM</Box>
                      <Box fontWeight="medium">Ticket resuelto - ID: #2341</Box>
                      <Box fontSize="sm" color="gray.600">Tiempo resolución: 45 min</Box>
                    </Box>
                    <Box p={4} borderBottom="1px" borderColor="gray.200">
                      <Box fontSize="xs" color="gray.500">11:00 AM</Box>
                      <Box fontWeight="medium">Chat iniciado - Consulta propiedades</Box>
                      <Box fontSize="sm" color="gray.600">Estado: En progreso</Box>
                    </Box>
                    <Box p={4}>
                      <Box fontSize="xs" color="gray.500">11:45 AM</Box>
                      <Box fontWeight="medium">Escalación a supervisor</Box>
                      <Box fontSize="sm" color="gray.600">Ticket: #2345</Box>
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
      title="Dashboard de Atención al Cliente"
      description="Centro de atención y soporte al cliente"
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
