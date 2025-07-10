import { Grid, GridItem, Box, Heading, Badge, Button, HStack, Text } from '@chakra-ui/react'
import { RoleDashboard } from '../Common/RoleDashboard'

export const SupervisorDashboard = () => {
  return (
    <RoleDashboard
      title="Dashboard de Supervisor"
      description="Gestión y monitoreo de equipo de agentes"
    >
      <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={8}>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Agentes a Cargo</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">8</Text>
            <Text fontSize="sm" color="green.400" mt={1}>↑ 2 nuevos (30 días)</Text>
          </Box>
        </GridItem>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Ventas del Equipo</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">$89,500</Text>
            <Text fontSize="sm" color="green.400" mt={1}>↑ 12% (30 días)</Text>
          </Box>
        </GridItem>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Propiedades Gestionadas</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">24</Text>
            <Text fontSize="sm" color="green.400" mt={1}>↑ 6% (30 días)</Text>
          </Box>
        </GridItem>
      </Grid>

      <Box mb={8}>
        <HStack justify="space-between" mb={4}>
          <Heading size="md" color="text">Rendimiento de Agentes</Heading>
          <Button size="sm" colorScheme="blue">Ver Detalles</Button>
        </HStack>
        <Box bg="bg.surface" borderRadius="lg" overflow="hidden" border="1px" borderColor="border">
          <Box as="table" w="100%" borderCollapse="collapse">
            <Box as="thead" bg="bg.muted">
              <Box as="tr">
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Agente
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Ventas
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Clientes
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Estado
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Rendimiento
                </Box>
              </Box>
            </Box>
            <Box as="tbody">
              <Box as="tr">
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Ana Fernández</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">$12,500</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">15</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted">
                  <Badge colorScheme="green">Activo</Badge>
                </Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">95%</Box>
              </Box>
              <Box as="tr">
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Roberto Silva</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">$8,900</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">12</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted">
                  <Badge colorScheme="green">Activo</Badge>
                </Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">88%</Box>
              </Box>
              <Box as="tr">
                <Box as="td" px={4} py={3} color="text">Carmen López</Box>
                <Box as="td" px={4} py={3} color="text">$15,200</Box>
                <Box as="td" px={4} py={3} color="text">18</Box>
                <Box as="td" px={4} py={3}>
                  <Badge colorScheme="green">Activo</Badge>
                </Box>
                <Box as="td" px={4} py={3} color="text">92%</Box>
              </Box>
            </Box>
          </Box>
        </Box>
      </Box>

      <Box>
        <Heading size="md" mb={4} color="text">Objetivos del Mes</Heading>
        <Box bg="bg.surface" p={6} borderRadius="lg" border="1px" borderColor="border">
          <Grid templateColumns="repeat(2, 1fr)" gap={6}>
            <GridItem>
              <Box>
                <Text fontSize="sm" color="text.muted" mb={2}>Meta de Ventas</Text>
                <Text fontSize="xl" fontWeight="bold" color="text">$100,000</Text>
                <Text fontSize="sm" color="blue.400" mt={1}>Progreso: $89,500 (89.5%)</Text>
              </Box>
            </GridItem>
            <GridItem>
              <Box>
                <Text fontSize="sm" color="text.muted" mb={2}>Nuevos Clientes</Text>
                <Text fontSize="xl" fontWeight="bold" color="text">50</Text>
                <Text fontSize="sm" color="green.400" mt={1}>Logrado: 45 (90%)</Text>
              </Box>
            </GridItem>
          </Grid>
        </Box>
      </Box>
    </RoleDashboard>
  )
} 
