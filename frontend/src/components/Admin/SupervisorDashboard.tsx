import { Grid, GridItem,     Table, Thead, Tbody, Tr, Th, Td, Box, Heading, Progress, Text } from '@chakra-ui/react'
import { RoleDashboard } from '../Common/RoleDashboard'

export const SupervisorDashboard = () => {
  return (
    <RoleDashboard
      title="Dashboard de Equipo"
      description="Gestión y monitoreo del equipo de agentes"
    >
      <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={8}>
        <GridItem>
          <Box>
            <Box>Ventas del Equipo</StatLabel>
            <Box>$123,456</StatNumber>
            <Box>↑ 12.5% (30 días)</StatHelpText>
          </Box>
        </GridItem>
        <GridItem>
          <Box>
            <Box>Propiedades Activas</StatLabel>
            <Box>28</StatNumber>
            <Box>↑ 5% (30 días)</StatHelpText>
          </Box>
        </GridItem>
        <GridItem>
          <Box>
            <Box>Visitas Programadas</StatLabel>
            <Box>45</StatNumber>
            <Box>Esta semana</StatHelpText>
          </Box>
        </GridItem>
      </Grid>

      <Box mb={8}>
        <Heading size="md" mb={4}>Rendimiento de Agentes</Heading>
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Agente</Th>
              <Th>Objetivo</Th>
              <Th isNumeric>Ventas</Th>
              <Th isNumeric>Visitas</Th>
              <Th isNumeric>Conversiones</Th>
            </Tr>
          </Thead>
          <Tbody>
            <Tr>
              <Td>Carlos López</Td>
              <Td>
                <Progress value={85} size="sm" colorScheme="green" />
                <Text fontSize="sm" mt={1}>85%</Text>
              </Td>
              <Td isNumeric>$45,000</Td>
              <Td isNumeric>15</Td>
              <Td isNumeric>3</Td>
            </Tr>
            <Tr>
              <Td>Ana Martínez</Td>
              <Td>
                <Progress value={72} size="sm" colorScheme="yellow" />
                <Text fontSize="sm" mt={1}>72%</Text>
              </Td>
              <Td isNumeric>$38,500</Td>
              <Td isNumeric>12</Td>
              <Td isNumeric>2</Td>
            </Tr>
          </Tbody>
        </Table>
      </Box>

      <Box>
        <Heading size="md" mb={4}>Próximas Visitas</Heading>
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Fecha</Th>
              <Th>Cliente</Th>
              <Th>Propiedad</Th>
              <Th>Agente</Th>
            </Tr>
          </Thead>
          <Tbody>
            <Tr>
              <Td>2024-03-20</Td>
              <Td>Roberto Sánchez</Td>
              <Td>Casa Residencial</Td>
              <Td>Carlos López</Td>
            </Tr>
            <Tr>
              <Td>2024-03-21</Td>
              <Td>Laura Torres</Td>
              <Td>Apartamento Centro</Td>
              <Td>Ana Martínez</Td>
            </Tr>
          </Tbody>
        </Table>
      </Box>
    </RoleDashboard>
  )
} 
