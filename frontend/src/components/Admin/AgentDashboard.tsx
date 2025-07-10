import { Grid, GridItem, Box, Heading, Badge, Button, HStack, VStack, Text } from '@chakra-ui/react'
import { RoleDashboard } from '../Common/RoleDashboard'

export const AgentDashboard = () => {
  return (
    <RoleDashboard
      title="Dashboard de Agente"
      description="Gestión de propiedades y clientes"
    >
      <Grid templateColumns="repeat(4, 1fr)" gap={6} mb={8}>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Propiedades Activas</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">12</Text>
            <Text fontSize="sm" color="green.400" mt={1}>3 nuevas esta semana</Text>
          </Box>
        </GridItem>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Clientes Activos</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">28</Text>
            <Text fontSize="sm" color="blue.400" mt={1}>5 leads nuevos</Text>
          </Box>
        </GridItem>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Visitas Programadas</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">8</Text>
            <Text fontSize="sm" color="orange.400" mt={1}>Esta semana</Text>
          </Box>
        </GridItem>
        <GridItem>
          <Box p={6} bg="bg.surface" borderRadius="lg" shadow="sm" border="1px" borderColor="border">
            <Text fontSize="sm" color="text.muted" mb={2}>Ventas del Mes</Text>
            <Text fontSize="2xl" fontWeight="bold" color="text">$45,600</Text>
            <Text fontSize="sm" color="green.400" mt={1}>↑ 18% (30 días)</Text>
          </Box>
        </GridItem>
      </Grid>

      <Grid templateColumns="2fr 1fr" gap={6} mb={8}>
        <GridItem>
          <Box>
            <HStack justify="space-between" mb={4}>
              <Heading size="md" color="text">Propiedades Recientes</Heading>
              <Button size="sm" colorScheme="blue">Ver Todas</Button>
            </HStack>
            <Box bg="bg.surface" borderRadius="lg" overflow="hidden" border="1px" borderColor="border">
              <Box as="table" w="100%" borderCollapse="collapse">
                <Box as="thead" bg="bg.muted">
                  <Box as="tr">
                    <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                      Propiedad
                    </Box>
                    <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                      Precio
                    </Box>
                    <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                      Estado
                    </Box>
                    <Box as="th" px={4} py={3} textAlign="left" fontSize="sm" fontWeight="medium" color="text.muted" borderBottom="1px" borderColor="border.muted">
                      Cliente
                    </Box>
                  </Box>
                </Box>
                <Box as="tbody">
                  <Box as="tr">
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Casa Zona Norte</Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">$120,000</Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted">
                      <Badge colorScheme="green">Disponible</Badge>
                    </Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">María González</Box>
                  </Box>
                  <Box as="tr">
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Apartamento Centro</Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">$85,000</Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted">
                      <Badge colorScheme="yellow">En Negociación</Badge>
                    </Box>
                    <Box as="td" px={4} py={3} borderBottom="1px" borderColor="border.muted" color="text">Carlos Ruiz</Box>
                  </Box>
                  <Box as="tr">
                    <Box as="td" px={4} py={3} color="text">Casa Zona Sur</Box>
                    <Box as="td" px={4} py={3} color="text">$95,500</Box>
                    <Box as="td" px={4} py={3}>
                      <Badge colorScheme="red">Vendida</Badge>
                    </Box>
                    <Box as="td" px={4} py={3} color="text">Ana López</Box>
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
                  Agregar Propiedad
                </Button>
                <Button w="full" variant="outline" borderColor="border" color="text" size="sm">
                  Nuevo Cliente
                </Button>
                <Button w="full" variant="outline" borderColor="border" color="text" size="sm">
                  Programar Visita
                </Button>
                <Button w="full" variant="outline" borderColor="border" color="text" size="sm">
                  Generar Contrato
                </Button>
              </VStack>
            </Box>

            <Box>
              <Heading size="md" mb={4} color="text">Próximas Visitas</Heading>
              <Box bg="bg.surface" p={4} borderRadius="lg" border="1px" borderColor="border">
                <VStack spacing={3} align="stretch">
                  <HStack justify="space-between">
                    <Box>
                      <Text fontSize="sm" fontWeight="medium" color="text">Casa Zona Norte</Text>
                      <Text fontSize="xs" color="text.muted">María González</Text>
                    </Box>
                    <Text fontSize="xs" color="text.muted">14:00</Text>
                  </HStack>
                  <HStack justify="space-between">
                    <Box>
                      <Text fontSize="sm" fontWeight="medium" color="text">Apartamento Centro</Text>
                      <Text fontSize="xs" color="text.muted">Luis Mendoza</Text>
                    </Box>
                    <Text fontSize="xs" color="text.muted">16:30</Text>
                  </HStack>
                  <HStack justify="space-between">
                    <Box>
                      <Text fontSize="sm" fontWeight="medium" color="text">Casa Zona Este</Text>
                      <Text fontSize="xs" color="text.muted">Carmen Silva</Text>
                    </Box>
                    <Text fontSize="xs" color="text.muted">Mañana 10:00</Text>
                  </HStack>
                </VStack>
              </Box>
            </Box>

            <Box>
              <Heading size="md" mb={4} color="text">Objetivos del Mes</Heading>
              <Box bg="bg.surface" p={4} borderRadius="lg" border="1px" borderColor="border">
                <VStack spacing={3}>
                  <HStack justify="space-between" w="full">
                    <Text color="text.muted">Meta Ventas</Text>
                    <Text fontSize="sm" color="text">$50,000</Text>
                  </HStack>
                  <HStack justify="space-between" w="full">
                    <Text color="text.muted">Progreso</Text>
                    <Badge colorScheme="green">91%</Badge>
                  </HStack>
                  <HStack justify="space-between" w="full">
                    <Text color="text.muted">Nuevos Clientes</Text>
                    <Text fontSize="sm" color="text">15/20</Text>
                  </HStack>
                  <HStack justify="space-between" w="full">
                    <Text color="text.muted">Visitas</Text>
                    <Text fontSize="sm" color="text">24/30</Text>
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
