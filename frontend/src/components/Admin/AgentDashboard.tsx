import { Grid, GridItem, Stat, StatLabel, StatNumber, StatHelpText, Table, Thead, Tbody, Tr, Th, Td, Box, Heading, Badge, Button, HStack, Progress, Text } from '@chakra-ui/react'
import { RoleDashboard } from '../Common/RoleDashboard'

export const AgentDashboard = () => {
  return (
    <RoleDashboard
      title="Dashboard de Agente"
      description="Gestión de propiedades y clientes"
    >
      <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={8}>
        <GridItem>
          <Stat>
            <StatLabel>Ventas del Mes</StatLabel>
            <StatNumber>$45,000</StatNumber>
            <StatHelpText>↑ 12.5% (30 días)</StatHelpText>
          </Stat>
        </GridItem>
        <GridItem>
          <Stat>
            <StatLabel>Propiedades Activas</StatLabel>
            <StatNumber>8</StatNumber>
            <StatHelpText>2 Nuevas</StatHelpText>
          </Stat>
        </GridItem>
        <GridItem>
          <Stat>
            <StatLabel>Leads Activos</StatLabel>
            <StatNumber>15</StatNumber>
            <StatHelpText>5 Calientes</StatHelpText>
          </Stat>
        </GridItem>
      </Grid>

      <Box mb={8}>
        <HStack justify="space-between" mb={4}>
          <Heading size="md">Próximas Visitas</Heading>
          <Button size="sm" colorScheme="blue">Agendar Nueva</Button>
        </HStack>
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Fecha</Th>
              <Th>Cliente</Th>
              <Th>Propiedad</Th>
              <Th>Estado</Th>
              <Th>Acciones</Th>
            </Tr>
          </Thead>
          <Tbody>
            <Tr>
              <Td>2024-03-20</Td>
              <Td>Roberto Sánchez</Td>
              <Td>Casa Residencial</Td>
              <Td>
                <Badge colorScheme="green">Confirmada</Badge>
              </Td>
              <Td>
                <Button size="sm" colorScheme="blue">Detalles</Button>
              </Td>
            </Tr>
            <Tr>
              <Td>2024-03-21</Td>
              <Td>Laura Torres</Td>
              <Td>Apartamento Centro</Td>
              <Td>
                <Badge colorScheme="yellow">Pendiente</Badge>
              </Td>
              <Td>
                <Button size="sm" colorScheme="blue">Confirmar</Button>
              </Td>
            </Tr>
          </Tbody>
        </Table>
      </Box>

      <Box>
        <Heading size="md" mb={4}>Objetivos y Rendimiento</Heading>
        <Grid templateColumns="repeat(2, 1fr)" gap={6}>
          <GridItem>
            <Box p={4} borderWidth={1} borderRadius="md">
              <Text fontWeight="bold" mb={2}>Progreso Mensual</Text>
              <Box mb={4}>
                <Text mb={2}>Ventas</Text>
                <Progress value={75} size="sm" colorScheme="green" />
                <Text fontSize="sm" mt={1}>$45,000 / $60,000</Text>
              </Box>
              <Box mb={4}>
                <Text mb={2}>Visitas</Text>
                <Progress value={60} size="sm" colorScheme="blue" />
                <Text fontSize="sm" mt={1}>12 / 20</Text>
              </Box>
              <Box>
                <Text mb={2}>Conversiones</Text>
                <Progress value={40} size="sm" colorScheme="purple" />
                <Text fontSize="sm" mt={1}>2 / 5</Text>
              </Box>
            </Box>
          </GridItem>
          <GridItem>
            <Box p={4} borderWidth={1} borderRadius="md">
              <Text fontWeight="bold" mb={2}>Leads por Estado</Text>
              <Table variant="simple" size="sm">
                <Tbody>
                  <Tr>
                    <Td>Calientes</Td>
                    <Td isNumeric>5</Td>
                  </Tr>
                  <Tr>
                    <Td>Tibios</Td>
                    <Td isNumeric>7</Td>
                  </Tr>
                  <Tr>
                    <Td>Fríos</Td>
                    <Td isNumeric>3</Td>
                  </Tr>
                </Tbody>
              </Table>
            </Box>
          </GridItem>
        </Grid>
      </Box>
    </RoleDashboard>
  )
} 