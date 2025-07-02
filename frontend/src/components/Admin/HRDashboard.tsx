import { Grid, GridItem, Box, Heading, Badge, Button, HStack } from '@chakra-ui/react'
import { RoleDashboard } from '../Common/RoleDashboard'

export const HRDashboard = () => {
  return (
    <RoleDashboard
      title="Dashboard de Recursos Humanos"
      description="Gestión de empleados y talento humano"
    >
      <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={8}>
        <GridItem>
          <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
            <Box fontSize="sm" color="gray.600" mb={2}>Total Empleados</Box>
            <Box fontSize="2xl" fontWeight="bold" color="gray.900">156</Box>
            <Box fontSize="sm" color="green.500" mt={1}>↑ 8% (30 días)</Box>
          </Box>
        </GridItem>
        <GridItem>
          <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
            <Box fontSize="sm" color="gray.600" mb={2}>Vacantes Activas</Box>
            <Box fontSize="2xl" fontWeight="bold" color="gray.900">12</Box>
            <Box fontSize="sm" color="orange.500" mt={1}>3 Urgentes</Box>
          </Box>
        </GridItem>
        <GridItem>
          <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
            <Box fontSize="sm" color="gray.600" mb={2}>Capacitaciones</Box>
            <Box fontSize="2xl" fontWeight="bold" color="gray.900">8</Box>
            <Box fontSize="sm" color="blue.500" mt={1}>Este mes</Box>
          </Box>
        </GridItem>
      </Grid>

      <Box mb={8}>
        <HStack justify="space-between" mb={4}>
          <Heading size="md">Empleados Recientes</Heading>
          <Button size="sm" colorScheme="blue">Ver Todos</Button>
        </HStack>
        <Box bg="white" borderRadius="lg" overflow="hidden" border="1px" borderColor="gray.200">
          <Box as="table" w="100%" borderCollapse="collapse">
            <Box as="thead" bg="gray.50">
              <Box as="tr">
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                  Empleado
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                  Cargo
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                  Departamento
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                  Estado
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                  Fecha Ingreso
                </Box>
              </Box>
            </Box>
            <Box as="tbody">
              <Box as="tr">
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="gray.200">Andrea López</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="gray.200">Agente Inmobiliario</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="gray.200">Ventas</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="gray.200">
                  <Badge colorScheme="green">Activo</Badge>
                </Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="gray.200">2024-03-15</Box>
              </Box>
              <Box as="tr">
                <Box as="td" px={4} py={3}>Carlos Ruiz</Box>
                <Box as="td" px={4} py={3}>Supervisor</Box>
                <Box as="td" px={4} py={3}>Operaciones</Box>
                <Box as="td" px={4} py={3}>
                  <Badge colorScheme="green">Activo</Badge>
                </Box>
                <Box as="td" px={4} py={3}>2024-03-10</Box>
              </Box>
            </Box>
          </Box>
        </Box>
      </Box>

      <Box>
        <Heading size="md" mb={4}>Evaluaciones Pendientes</Heading>
        <Box bg="white" borderRadius="lg" overflow="hidden" border="1px" borderColor="gray.200">
          <Box as="table" w="100%" borderCollapse="collapse">
            <Box as="thead" bg="gray.50">
              <Box as="tr">
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                  Empleado
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                  Tipo
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                  Fecha Límite
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                  Prioridad
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="gray.700" borderBottom="1px" borderColor="gray.200">
                  Acciones
                </Box>
              </Box>
            </Box>
            <Box as="tbody">
              <Box as="tr">
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="gray.200">Juan Martínez</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="gray.200">Evaluación Anual</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="gray.200">2024-03-25</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="gray.200">
                  <Badge colorScheme="red">Alta</Badge>
                </Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="gray.200">
                  <Button size="sm" colorScheme="blue">Evaluar</Button>
                </Box>
              </Box>
              <Box as="tr">
                <Box as="td" px={4} py={3}>Laura Sánchez</Box>
                <Box as="td" px={4} py={3}>Evaluación Trimestral</Box>
                <Box as="td" px={4} py={3}>2024-03-30</Box>
                <Box as="td" px={4} py={3}>
                  <Badge colorScheme="orange">Media</Badge>
                </Box>
                <Box as="td" px={4} py={3}>
                  <Button size="sm" colorScheme="blue">Evaluar</Button>
                </Box>
              </Box>
            </Box>
          </Box>
        </Box>
      </Box>
    </RoleDashboard>
  )
} 
