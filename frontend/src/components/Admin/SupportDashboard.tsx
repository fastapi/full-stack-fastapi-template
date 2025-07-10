import { Grid, GridItem, Box, Heading, Badge, Button, HStack, VStack, Text } from '@chakra-ui/react'
import { RoleDashboard } from '../Common/RoleDashboard'

export const SupportDashboard = () => {
  return (
    <RoleDashboard
      title="Dashboard de Atención al Cliente"
      description="Gestión de tickets y soporte a clientes"
    >
      <Grid templateColumns="repeat(4, 1fr)" gap={6} mb={8}>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Tickets Abiertos</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">23</Text>
            <Text fontSize="sm" color="orange.400" mt={1}>5 urgentes</Text>
          </Box>
        </GridItem>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Tickets Resueltos</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">187</Text>
            <Text fontSize="sm" color="green.400" mt={1}>Este mes</Text>
          </Box>
        </GridItem>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Tiempo Promedio</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">2.5h</Text>
            <Text fontSize="sm" color="blue.400" mt={1}>Resolución</Text>
          </Box>
        </GridItem>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Satisfacción</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">4.8</Text>
            <Text fontSize="sm" color="green.400" mt={1}>de 5.0</Text>
          </Box>
        </GridItem>
      </Grid>

      <Grid templateColumns="2fr 1fr" gap={6} mb={8}>
        <GridItem>
          <Box>
            <HStack justify="space-between" mb={4}>
              <Heading size="md" color="text">Tickets Recientes</Heading>
              <Button size="sm" colorScheme="blue">Ver Todos</Button>
            </HStack>
            <Box bg="bg.surface" borderRadius="lg" overflow="hidden" border="1px" borderColor="border">
              <Box as="table" w="100%" borderCollapse="collapse">
                <Box as="thead" bg="bg.muted">
                  <Box as="tr">
                    <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                      ID
                    </Box>
                    <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                      Cliente
                    </Box>
                    <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                      Asunto
                    </Box>
                    <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                      Estado
                    </Box>
                    <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                      Prioridad
                    </Box>
                  </Box>
                </Box>
                <Box as="tbody">
                  <Box as="tr">
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">#1234</Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">María García</Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Consulta sobre documentos</Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted">
                      <Badge colorScheme="yellow">En Proceso</Badge>
                    </Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted">
                      <Badge colorScheme="red">Alta</Badge>
                    </Box>
                  </Box>
                  <Box as="tr">
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">#1235</Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Carlos Ruiz</Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Problema con cita</Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted">
                      <Badge colorScheme="blue">Nuevo</Badge>
                    </Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted">
                      <Badge colorScheme="orange">Media</Badge>
                    </Box>
                  </Box>
                  <Box as="tr">
                    <Box as="td" px={4} py={3} color="text">#1236</Box>
                    <Box as="td" px={4} py={3} color="text">Ana López</Box>
                    <Box as="td" px={4} py={3} color="text">Información de propiedad</Box>
                    <Box as="td" px={4} py={3}>
                      <Badge colorScheme="green">Resuelto</Badge>
                    </Box>
                    <Box as="td" px={4} py={3}>
                      <Badge colorScheme="green">Baja</Badge>
                    </Box>
                  </Box>
                </Box>
              </Box>
            </Box>
          </Box>
        </GridItem>

        <GridItem>
          <VStack spacing={6} align="stretch">
            <Box>
              <Heading size="md" mb={4} color="text">Acciones Rápidas</Heading>
              <VStack spacing={3}>
                <Button w="full" colorScheme="blue" size="sm">
                  Nuevo Ticket
                </Button>
                <Button w="full" variant="outline" borderColor="border" color="text" size="sm">
                  Ver Cola de Tickets
                </Button>
                <Button w="full" variant="outline" borderColor="border" color="text" size="sm">
                  Reportes de Satisfacción
                </Button>
                <Button w="full" variant="outline" borderColor="border" color="text" size="sm">
                  Base de Conocimientos
                </Button>
              </VStack>
            </Box>

            <Box>
              <Heading size="md" mb={4} color="text">Estado de la Cola</Heading>
              <Box bg="bg.surface" p={4} borderRadius="lg" border="1px" borderColor="border">
                <VStack spacing={3}>
                  <HStack justify="space-between" w="full">
                    <Text color="text.muted">Nuevos</Text>
                    <Badge colorScheme="blue">8</Badge>
                  </HStack>
                  <HStack justify="space-between" w="full">
                    <Text color="text.muted">En Proceso</Text>
                    <Badge colorScheme="yellow">15</Badge>
                  </HStack>
                  <HStack justify="space-between" w="full">
                    <Text color="text.muted">Esperando Cliente</Text>
                    <Badge colorScheme="orange">5</Badge>
                  </HStack>
                  <HStack justify="space-between" w="full">
                    <Text color="text.muted">Resueltos Hoy</Text>
                    <Badge colorScheme="green">12</Badge>
                  </HStack>
                </VStack>
              </Box>
            </Box>
          </VStack>
        </GridItem>
      </Grid>
    </RoleDashboard>
  )
} 
