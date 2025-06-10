import { Grid, GridItem, Stat, StatLabel, StatNumber, StatHelpText, Table, Thead, Tbody, Tr, Th, Td, Box, Heading } from '@chakra-ui/react'
import { RoleDashboard } from '../Common/RoleDashboard'

export const ManagerDashboard = () => {
  return (
    <RoleDashboard
      title="Dashboard de Sucursal"
      description="Gestión y monitoreo de la sucursal"
    >
      <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={8}>
        <GridItem>
          <Stat>
            <StatLabel>Ventas del Mes</StatLabel>
            <StatNumber>$234,567</StatNumber>
            <StatHelpText>↑ 15.36% (30 días)</StatHelpText>
          </Stat>
        </GridItem>
        <GridItem>
          <Stat>
            <StatLabel>Propiedades Activas</StatLabel>
            <StatNumber>45</StatNumber>
            <StatHelpText>↑ 8% (30 días)</StatHelpText>
          </Stat>
        </GridItem>
        <GridItem>
          <Stat>
            <StatLabel>Agentes Activos</StatLabel>
            <StatNumber>12</StatNumber>
            <StatHelpText>↑ 2% (30 días)</StatHelpText>
          </Stat>
        </GridItem>
      </Grid>

      <Box>
        <Heading size="md" mb={4}>Rendimiento de Supervisores</Heading>
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Supervisor</Th>
              <Th isNumeric>Ventas</Th>
              <Th isNumeric>Equipo</Th>
              <Th isNumeric>Rendimiento</Th>
            </Tr>
          </Thead>
          <Tbody>
            <Tr>
              <Td>Juan Pérez</Td>
              <Td isNumeric>$45,000</Td>
              <Td isNumeric>5</Td>
              <Td isNumeric>92%</Td>
            </Tr>
            <Tr>
              <Td>María García</Td>
              <Td isNumeric>$38,500</Td>
              <Td isNumeric>4</Td>
              <Td isNumeric>88%</Td>
            </Tr>
          </Tbody>
        </Table>
      </Box>
    </RoleDashboard>
  )
} 