import { useState } from 'react'
import { Grid, GridItem, Box, Heading, Button, Flex } from '@chakra-ui/react'
import { FiHome, FiBarChart2, FiUsers, FiEye } from 'react-icons/fi'
import { RoleDashboard } from '../Common/RoleDashboard'
import { PropertyCRM } from './PropertyCRM'

export const SupervisorDashboard = () => {
  const [activeTab, setActiveTab] = useState('dashboard')

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: FiBarChart2 },
    { id: 'properties', label: 'Propiedades', icon: FiHome },
    { id: 'supervision', label: 'Supervisión', icon: FiEye },
    { id: 'agents', label: 'Agentes', icon: FiUsers }
  ]

  const renderContent = () => {
    switch (activeTab) {
      case 'properties':
        return <PropertyCRM />
      case 'supervision':
        return (
          <Box>
            <Heading size="md" mb={4}>Panel de Supervisión</Heading>
            <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
              <Box fontSize="lg" color="gray.600" textAlign="center">
                Módulo de supervisión y control en desarrollo
              </Box>
            </Box>
          </Box>
        )
      case 'agents':
        return (
          <Box>
            <Heading size="md" mb={4}>Gestión de Agentes</Heading>
            <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
              <Box fontSize="lg" color="gray.600" textAlign="center">
                Módulo de gestión de agentes en desarrollo
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
                  <Box fontSize="sm" color="gray.600" mb={2}>Agentes Supervisados</Box>
                  <Box fontSize="2xl" fontWeight="bold" color="gray.900">8</Box>
                  <Box fontSize="sm" color="blue.500" mt={1}>↑ 1 nuevo agente</Box>
                </Box>
              </GridItem>
              <GridItem>
                <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
                  <Box fontSize="sm" color="gray.600" mb={2}>Ventas del Equipo</Box>
                  <Box fontSize="2xl" fontWeight="bold" color="gray.900">$89,432</Box>
                  <Box fontSize="sm" color="green.500" mt={1}>↑ 22% (30 días)</Box>
                </Box>
              </GridItem>
              <GridItem>
                <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
                  <Box fontSize="sm" color="gray.600" mb={2}>Propiedades Asignadas</Box>
                  <Box fontSize="2xl" fontWeight="bold" color="gray.900">24</Box>
                  <Box fontSize="sm" color="green.500" mt={1}>↑ 12% (30 días)</Box>
                </Box>
              </GridItem>
            </Grid>

            <Box>
              <Heading size="md" mb={4}>Rendimiento de Agentes</Heading>
              <Box bg="white" borderRadius="lg" overflow="hidden" border="1px" borderColor="gray.200">
                <Box as="table" w="100%" borderCollapse="collapse">
                  <Box as="thead" bg="gray.50">
                    <Box as="tr">
                      <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                        Agente
                      </Box>
                      <Box as="th" px={4} py={3} textAlign="right" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                        Ventas
                      </Box>
                      <Box as="th" px={4} py={3} textAlign="right" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                        Clientes
                      </Box>
                      <Box as="th" px={4} py={3} textAlign="right" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                        Efectividad
                      </Box>
                    </Box>
                  </Box>
                  <Box as="tbody">
                    <Box as="tr">
                      <Box as="td" px={4} py={3} borderBottom="1px" borderColor="gray.200">Carlos Ruiz</Box>
                      <Box as="td" px={4} py={3} textAlign="right" borderBottom="1px" borderColor="gray.200">$28,500</Box>
                      <Box as="td" px={4} py={3} textAlign="right" borderBottom="1px" borderColor="gray.200">15</Box>
                      <Box as="td" px={4} py={3} textAlign="right" borderBottom="1px" borderColor="gray.200">85%</Box>
                    </Box>
                    <Box as="tr">
                      <Box as="td" px={4} py={3} borderBottom="1px" borderColor="gray.200">Ana López</Box>
                      <Box as="td" px={4} py={3} textAlign="right" borderBottom="1px" borderColor="gray.200">$31,200</Box>
                      <Box as="td" px={4} py={3} textAlign="right" borderBottom="1px" borderColor="gray.200">18</Box>
                      <Box as="td" px={4} py={3} textAlign="right" borderBottom="1px" borderColor="gray.200">92%</Box>
                    </Box>
                    <Box as="tr">
                      <Box as="td" px={4} py={3}>Luis Mendoza</Box>
                      <Box as="td" px={4} py={3} textAlign="right">$22,800</Box>
                      <Box as="td" px={4} py={3} textAlign="right">12</Box>
                      <Box as="td" px={4} py={3} textAlign="right">78%</Box>
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
      title="Dashboard de Supervisor"
      description="Supervisión y control de equipos de ventas"
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
