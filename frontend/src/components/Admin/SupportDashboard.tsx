import { Grid, GridItem,     Table, Thead, Tbody, Tr, Th, Td, Box, Heading, Badge, Button, HStack, Text } from '@chakra-ui/react'
import { RoleDashboard } from '../Common/RoleDashboard'

export const SupportDashboard = () => {
  return (
    <RoleDashboard
      title="Dashboard de Atención al Cliente"
      description="Gestión de tickets y soporte"
    >
      <Grid templateColumns="repeat(3, 1fr)" gap={6} mb={8}>
        <GridItem>
          <Box>
            <Box>Tickets Abiertos</StatLabel>
            <Box>24</StatNumber>
            <Box>5 Urgentes</StatHelpText>
          </Box>
        </GridItem>
        <GridItem>
          <Box>
            <Box>Tiempo Promedio</StatLabel>
            <Box>2.5h</StatNumber>
            <Box>↓ 15% (30 días)</StatHelpText>
          </Box>
        </GridItem>
        <GridItem>
          <Box>
            <Box>Satisfacción</StatLabel>
            <Box>4.8/5</StatNumber>
            <Box>↑ 0.2 (30 días)</StatHelpText>
          </Box>
        </GridItem>
      </Grid>

      <Box mb={8}>
        <HStack justify="space-between" mb={4}>
          <Heading size="md">Tickets Prioritarios</Heading>
          <Button size="sm" colorScheme="blue">Ver Todos</Button>
        </HStack>
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>ID</Th>
              <Th>Cliente</Th>
              <Th>Asunto</Th>
              <Th>Prioridad</Th>
              <Th>Estado</Th>
              <Th>Acciones</Th>
            </Tr>
          </Thead>
          <Tbody>
            <Tr>
              <Td>#1234</Td>
              <Td>Roberto Sánchez</Td>
              <Td>Problema con contrato</Td>
              <Td>
                <Badge colorScheme="red">Alta</Badge>
              </Td>
              <Td>
                <Badge colorScheme="yellow">En Proceso</Badge>
              </Td>
              <Td>
                <Button size="sm" colorScheme="blue">Atender</Button>
              </Td>
            </Tr>
            <Tr>
              <Td>#1235</Td>
              <Td>Laura Torres</Td>
              <Td>Consulta de pago</Td>
              <Td>
                <Badge colorScheme="orange">Media</Badge>
              </Td>
              <Td>
                <Badge colorScheme="green">Resuelto</Badge>
              </Td>
              <Td>
                <Button size="sm" colorScheme="blue">Ver Detalles</Button>
              </Td>
            </Tr>
          </Tbody>
        </Table>
      </Box>

      <Box>
        <Heading size="md" mb={4}>Métricas de Servicio</Heading>
        <Grid templateColumns="repeat(2, 1fr)" gap={6}>
          <GridItem>
            <Box p={4} borderWidth={1} borderRadius="md">
              <Text fontWeight="bold" mb={2}>Tickets por Categoría</Text>
              <Table variant="simple" size="sm">
                <Tbody>
                  <Tr>
                    <Td>Contratos</Td>
                    <Td isNumeric>45%</Td>
                  </Tr>
                  <Tr>
                    <Td>Pagos</Td>
                    <Td isNumeric>30%</Td>
                  </Tr>
                  <Tr>
                    <Td>Otros</Td>
                    <Td isNumeric>25%</Td>
                  </Tr>
                </Tbody>
              </Table>
            </Box>
          </GridItem>
          <GridItem>
            <Box p={4} borderWidth={1} borderRadius="md">
              <Text fontWeight="bold" mb={2}>Tiempo de Respuesta</Text>
              <Table variant="simple" size="sm">
                <Tbody>
                  <Tr>
                    <Td>Alta Prioridad</Td>
                    <Td isNumeric>1.2h</Td>
                  </Tr>
                  <Tr>
                    <Td>Media Prioridad</Td>
                    <Td isNumeric>2.5h</Td>
                  </Tr>
                  <Tr>
                    <Td>Baja Prioridad</Td>
                    <Td isNumeric>4.0h</Td>
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
