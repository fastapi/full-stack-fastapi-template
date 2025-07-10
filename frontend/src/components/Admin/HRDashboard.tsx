import { Grid, GridItem, Box, Heading, Badge, Button, HStack, Text } from '@chakra-ui/react'
import { RoleDashboard } from '../Common/RoleDashboard'

export const HRDashboard = () => {
  return (
    <RoleDashboard
      title="Dashboard de Recursos Humanos"
      description="Gestión de empleados y talento humano"
    >
      <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={8}>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Total Empleados</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">156</Text>
            <Text fontSize="sm" color="green.400" mt={1}>↑ 8% (30 días)</Text>
          </Box>
        </GridItem>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Vacantes Activas</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">12</Text>
            <Text fontSize="sm" color="orange.400" mt={1}>3 Urgentes</Text>
          </Box>
        </GridItem>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Capacitaciones</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">8</Text>
            <Text fontSize="sm" color="blue.400" mt={1}>Este mes</Text>
          </Box>
        </GridItem>
      </Grid>

      <Box mb={8}>
        <HStack justify="space-between" mb={4}>
          <Heading size="md" color="text">Empleados Recientes</Heading>
          <Button size="sm" colorScheme="blue">Ver Todos</Button>
        </HStack>
        <Box bg="bg.surface" borderRadius="lg" overflow="hidden" border="1px" borderColor="border">
          <Box as="table" w="100%" borderCollapse="collapse">
            <Box as="thead" bg="bg.muted">
              <Box as="tr">
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Empleado
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Cargo
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Departamento
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Estado
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Fecha Ingreso
                </Box>
              </Box>
            </Box>
            <Box as="tbody">
              <Box as="tr">
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Andrea López</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Agente Inmobiliario</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Ventas</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted">
                  <Badge colorScheme="green">Activo</Badge>
                </Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">2024-03-15</Box>
              </Box>
              <Box as="tr">
                <Box as="td" px={4} py={3} color="text">Carlos Ruiz</Box>
                <Box as="td" px={4} py={3} color="text">Supervisor</Box>
                <Box as="td" px={4} py={3} color="text">Operaciones</Box>
                <Box as="td" px={4} py={3}>
                  <Badge colorScheme="green">Activo</Badge>
                </Box>
                <Box as="td" px={4} py={3} color="text">2024-03-10</Box>
              </Box>
            </Box>
          </Box>
        </Box>
      </Box>

      <Box>
        <Heading size="md" mb={4} color="text">Evaluaciones Pendientes</Heading>
        <Box bg="bg.surface" borderRadius="lg" overflow="hidden" border="1px" borderColor="border">
          <Box as="table" w="100%" borderCollapse="collapse">
            <Box as="thead" bg="bg.muted">
              <Box as="tr">
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Empleado
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Tipo
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Fecha Límite
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Prioridad
                </Box>
                <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                  Acciones
                </Box>
              </Box>
            </Box>
            <Box as="tbody">
              <Box as="tr">
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Juan Martínez</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Evaluación Anual</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">2024-03-25</Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted">
                  <Badge colorScheme="red">Alta</Badge>
                </Box>
                <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted">
                  <Button size="sm" colorScheme="blue">Evaluar</Button>
                </Box>
              </Box>
              <Box as="tr">
                <Box as="td" px={4} py={3} color="text">Laura Sánchez</Box>
                <Box as="td" px={4} py={3} color="text">Evaluación Trimestral</Box>
                <Box as="td" px={4} py={3} color="text">2024-03-30</Box>
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
