import { Grid, GridItem,     Table, Thead, Tbody, Tr, Th, Td, Box, Heading } from '@chakra-ui/react'
import { RoleDashboard } from '../Common/RoleDashboard'

export const ManagerDashboard = () => {
  return (
    <RoleDashboard
      title="Dashboard de Sucursal"
      description="Gestión y monitoreo de la sucursal"
    >
      <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={8}>
        <GridItem>
          <Box>
            <Box>Ventas del Mes</StatLabel>
            <Box>$234,567</StatNumber>
            <Box>↑ 15.36% (30 días)</StatHelpText>
          </Box>
        </GridItem>
        <GridItem>
          <Box>
            <Box>Propiedades Activas</StatLabel>
            <Box>45</StatNumber>
            <Box>↑ 8% (30 días)</StatHelpText>
          </Box>
        </GridItem>
        <GridItem>
          <Box>
            <Box>Agentes Activos</StatLabel>
            <Box>12</StatNumber>
            <Box>↑ 2% (30 días)</StatHelpText>
          </Box>
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
