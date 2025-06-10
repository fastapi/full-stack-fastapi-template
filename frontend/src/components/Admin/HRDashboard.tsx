import { Grid, GridItem, Stat, StatLabel, StatNumber, StatHelpText, Table, Thead, Tbody, Tr, Th, Td, Box, Heading, Badge, Button, HStack } from '@chakra-ui/react'
import { RoleDashboard } from '../Common/RoleDashboard'

export const HRDashboard = () => {
  return (
    <RoleDashboard
      title="Dashboard de Recursos Humanos"
      description="Gestión de personal y recursos humanos"
    >
      <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={8}>
        <GridItem>
          <Stat>
            <StatLabel>Total Empleados</StatLabel>
            <StatNumber>156</StatNumber>
            <StatHelpText>↑ 8% (30 días)</StatHelpText>
          </Stat>
        </GridItem>
        <GridItem>
          <Stat>
            <StatLabel>Vacantes Activas</StatLabel>
            <StatNumber>12</StatNumber>
            <StatHelpText>3 Urgentes</StatHelpText>
          </Stat>
        </GridItem>
        <GridItem>
          <Stat>
            <StatLabel>Capacitaciones</StatLabel>
            <StatNumber>8</StatNumber>
            <StatHelpText>Este mes</StatHelpText>
          </Stat>
        </GridItem>
      </Grid>

      <Box mb={8}>
        <HStack justify="space-between" mb={4}>
          <Heading size="md">Solicitudes Pendientes</Heading>
          <Button size="sm" colorScheme="blue">Ver Todas</Button>
        </HStack>
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Empleado</Th>
              <Th>Tipo</Th>
              <Th>Fecha</Th>
              <Th>Estado</Th>
              <Th>Acciones</Th>
            </Tr>
          </Thead>
          <Tbody>
            <Tr>
              <Td>Juan Pérez</Td>
              <Td>Vacaciones</Td>
              <Td>2024-04-01</Td>
              <Td>
                <Badge colorScheme="yellow">Pendiente</Badge>
              </Td>
              <Td>
                <Button size="sm" colorScheme="green" mr={2}>Aprobar</Button>
                <Button size="sm" colorScheme="red">Rechazar</Button>
              </Td>
            </Tr>
            <Tr>
              <Td>María García</Td>
              <Td>Permiso Médico</Td>
              <Td>2024-03-25</Td>
              <Td>
                <Badge colorScheme="yellow">Pendiente</Badge>
              </Td>
              <Td>
                <Button size="sm" colorScheme="green" mr={2}>Aprobar</Button>
                <Button size="sm" colorScheme="red">Rechazar</Button>
              </Td>
            </Tr>
          </Tbody>
        </Table>
      </Box>

      <Box>
        <Heading size="md" mb={4}>Próximas Capacitaciones</Heading>
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Curso</Th>
              <Th>Instructor</Th>
              <Th>Fecha</Th>
              <Th>Participantes</Th>
              <Th>Estado</Th>
            </Tr>
          </Thead>
          <Tbody>
            <Tr>
              <Td>Ventas Avanzadas</Td>
              <Td>Carlos Ruiz</Td>
              <Td>2024-03-25</Td>
              <Td>15/20</Td>
              <Td>
                <Badge colorScheme="green">Confirmado</Badge>
              </Td>
            </Tr>
            <Tr>
              <Td>Negociación</Td>
              <Td>Ana Martínez</Td>
              <Td>2024-03-28</Td>
              <Td>12/15</Td>
              <Td>
                <Badge colorScheme="yellow">Pendiente</Badge>
              </Td>
            </Tr>
          </Tbody>
        </Table>
      </Box>
    </RoleDashboard>
  )
} 