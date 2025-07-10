import { useState } from 'react'
import { Grid, GridItem, Box, Heading, Button, Flex, Text } from '@chakra-ui/react'
import { FiHome, FiBarChart2, FiUsers } from 'react-icons/fi'
import { RoleDashboard } from '../Common/RoleDashboard'
import { PropertyCRM } from './PropertyCRM'

export const ManagerDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard')

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: FiBarChart2 },
    { id: 'properties', label: 'Propiedades', icon: FiHome },
    { id: 'team', label: 'Equipo', icon: FiUsers }
  ]

  const renderContent = () => {
    switch (activeTab) {
      case 'properties':
        return <PropertyCRM />
      case 'team':
        return (
          <Box>
            <Heading size="md" mb={4} color="text">Gestión de Equipo</Heading>
            <Box bg="bg.surface" p={6} borderRadius="lg" shadow="sm" border="1px" borderColor="border">
              <Text fontSize="lg" color="text.muted" textAlign="center">
                Módulo de gestión de equipo en desarrollo
              </Text>
            </Box>
          </Box>
        )
      default:
        return (
          <>
            <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={8}>
              <GridItem>
                <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
                  <Text fontSize="sm" color="text.muted" mb={2}>Ventas del Mes</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="text">$234,567</Text>
                  <Text fontSize="sm" color="green.400" mt={1}>↑ 15.36% (30 días)</Text>
                </Box>
              </GridItem>
              <GridItem>
                <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
                  <Text fontSize="sm" color="text.muted" mb={2}>Propiedades Activas</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="text">45</Text>
                  <Text fontSize="sm" color="green.400" mt={1}>↑ 8% (30 días)</Text>
                </Box>
              </GridItem>
              <GridItem>
                <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
                  <Text fontSize="sm" color="text.muted" mb={2}>Agentes Activos</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="text">12</Text>
                  <Text fontSize="sm" color="green.400" mt={1}>↑ 2% (30 días)</Text>
                </Box>
              </GridItem>
            </Grid>

            <Box>
              <Heading size="md" mb={4} color="text">Rendimiento de Supervisores</Heading>
              <Box bg="bg.surface" borderRadius="lg" overflow="hidden" border="1px" borderColor="border">
                <Box as="table" w="100%" borderCollapse="collapse">
                  <Box as="thead" bg="bg.muted">
                    <Box as="tr">
                      <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                        Supervisor
                      </Box>
                      <Box as="th" px={4} py={3} textAlign="right" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                        Ventas
                      </Box>
                      <Box as="th" px={4} py={3} textAlign="right" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                        Equipo
                      </Box>
                      <Box as="th" px={4} py={3} textAlign="right" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                        Rendimiento
                      </Box>
                    </Box>
                  </Box>
                  <Box as="tbody">
                    <Box as="tr">
                      <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Juan Pérez</Box>
                      <Box as="td" px={4} py={3} textAlign="right" borderBottom="1px" borderColor="border.muted" color="text">$45,000</Box>
                      <Box as="td" px={4} py={3} textAlign="right" borderBottom="1px" borderColor="border.muted" color="text">5</Box>
                      <Box as="td" px={4} py={3} textAlign="right" borderBottom="1px" borderColor="border.muted" color="text">92%</Box>
                    </Box>
                    <Box as="tr">
                      <Box as="td" px={4} py={3} color="text">María García</Box>
                      <Box as="td" px={4} py={3} textAlign="right" color="text">$38,500</Box>
                      <Box as="td" px={4} py={3} textAlign="right" color="text">4</Box>
                      <Box as="td" px={4} py={3} textAlign="right" color="text">88%</Box>
                    </Box>
                  </Box>
                </Box>
              </Box>
            </Box>
          </>
        )
    }
  }

  return (
    <RoleDashboard
      title="Dashboard de Manager"
      description="Gestión y monitoreo operativo"
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
