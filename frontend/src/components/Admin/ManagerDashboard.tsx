import { useState } from 'react'
import { Grid, GridItem, Box, Heading, Button, Flex } from '@chakra-ui/react'
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
            <Heading size="md" mb={4}>Gestión de Equipo</Heading>
            <Box bg="white" p={6} borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
              <Box fontSize="lg" color="gray.600" textAlign="center">
                Módulo de gestión de equipo en desarrollo
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
                  <Box fontSize="sm" color="gray.600" mb={2}>Ventas del Mes</Box>
                  <Box fontSize="2xl" fontWeight="bold" color="gray.900">$234,567</Box>
                  <Box fontSize="sm" color="green.500" mt={1}>↑ 15.36% (30 días)</Box>
                </Box>
              </GridItem>
              <GridItem>
                <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
                  <Box fontSize="sm" color="gray.600" mb={2}>Propiedades Activas</Box>
                  <Box fontSize="2xl" fontWeight="bold" color="gray.900">45</Box>
                  <Box fontSize="sm" color="green.500" mt={1}>↑ 8% (30 días)</Box>
                </Box>
              </GridItem>
              <GridItem>
                <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
                  <Box fontSize="sm" color="gray.600" mb={2}>Agentes Activos</Box>
                  <Box fontSize="2xl" fontWeight="bold" color="gray.900">12</Box>
                  <Box fontSize="sm" color="green.500" mt={1}>↑ 2% (30 días)</Box>
                </Box>
              </GridItem>
            </Grid>

            <Box>
              <Heading size="md" mb={4}>Rendimiento de Supervisores</Heading>
              <Box bg="white" borderRadius="lg" overflow="hidden" border="1px" borderColor="gray.200">
                <Box as="table" w="100%" borderCollapse="collapse">
                  <Box as="thead" bg="gray.50">
                    <Box as="tr">
                      <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                        Supervisor
                      </Box>
                      <Box as="th" px={4} py={3} textAlign="right" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                        Ventas
                      </Box>
                      <Box as="th" px={4} py={3} textAlign="right" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                        Equipo
                      </Box>
                      <Box as="th" px={4} py={3} textAlign="right" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                        Rendimiento
                      </Box>
                    </Box>
                  </Box>
                  <Box as="tbody">
                    <Box as="tr">
                      <Box as="td" px={4} py={3} borderBottom="1px" borderColor="gray.200">Juan Pérez</Box>
                      <Box as="td" px={4} py={3} textAlign="right" borderBottom="1px" borderColor="gray.200">$45,000</Box>
                      <Box as="td" px={4} py={3} textAlign="right" borderBottom="1px" borderColor="gray.200">5</Box>
                      <Box as="td" px={4} py={3} textAlign="right" borderBottom="1px" borderColor="gray.200">92%</Box>
                    </Box>
                    <Box as="tr">
                      <Box as="td" px={4} py={3}>María García</Box>
                      <Box as="td" px={4} py={3} textAlign="right">$38,500</Box>
                      <Box as="td" px={4} py={3} textAlign="right">4</Box>
                      <Box as="td" px={4} py={3} textAlign="right">88%</Box>
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
