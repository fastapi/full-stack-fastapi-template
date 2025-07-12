import { useState } from 'react';
import { 
  Box, 
  VStack, 
  HStack, 
  Heading, 
  Text,
  Select,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Button,
  Badge,
  useDisclosure,
  Icon,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  useStyleConfig
} from '@chakra-ui/react';

// Importar componentes de tabla desde @chakra-ui/table
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
} from '@chakra-ui/table';

// Importar componentes de modal desde @chakra-ui/modal
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
} from '@chakra-ui/modal';

// Importar useToast desde @chakra-ui/toast
import { useToast } from '@chakra-ui/toast';
import { FiDownload, FiFilter, FiBarChart2, FiDollarSign, FiHome, FiUsers, FiTrendingUp } from 'react-icons/fi';

type TimeRange = '7days' | '30days' | '90days' | '12months' | 'custom';
type ReportType = 'sales' | 'properties' | 'users' | 'financial' | 'all';

const Reports = () => {
  const [timeRange, setTimeRange] = useState<TimeRange>('30days');
  const [reportType, setReportType] = useState<ReportType>('all');
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  // Datos de ejemplo para los reportes
  const reportData = {
    totalSales: {
      value: 1245000,
      change: 12.5,
      isIncrease: true
    },
    newProperties: {
      value: 45,
      change: 8.2,
      isIncrease: true
    },
    newUsers: {
      value: 128,
      change: 3.1,
      isIncrease: true
    },
    revenue: {
      value: 3450000,
      change: 5.7,
      isIncrease: true
    },
    topProperties: [
      { id: 1, name: 'Casa en El Poblado', location: 'Medellín', price: 850000000, views: 1245, inquiries: 45 },
      { id: 2, name: 'Apartamento en Laureles', location: 'Medellín', price: 420000000, views: 987, inquiries: 32 },
      { id: 3, name: 'Finca en Rionegro', location: 'Rionegro', price: 1250000000, views: 756, inquiries: 28 },
    ],
    userActivity: [
      { id: 1, name: 'Juan Pérez', role: 'Agente', actions: 245, lastActive: 'hace 2 horas' },
      { id: 2, name: 'María Gómez', role: 'Cliente', actions: 132, lastActive: 'hace 5 horas' },
      { id: 3, name: 'Carlos López', role: 'Administrador', actions: 89, lastActive: 'hace 1 día' },
    ]
  };

  const handleGenerateReport = () => {
    // Lógica para generar el reporte
    onOpen();
  };

  const handleDownloadReport = (format: 'pdf' | 'excel' | 'csv') => {
    toast({
      title: 'Reporte generado',
      description: `El reporte se ha generado en formato ${format.toUpperCase()} y está listo para descargar.`,
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  return (
    <Box p={6}>
      <VStack align="stretch" spacing={6}>
        {/* Encabezado */}
        <HStack justify="space-between" align="center">
          <Box>
            <Heading size="lg" mb={2}>Reportes y Análisis</Heading>
            <Text color="gray.500">Genera y descarga informes detallados del sistema</Text>
          </Box>
          <HStack spacing={4}>
            <Select 
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as TimeRange)}
              width="200px"
            >
              <option value="7days">Últimos 7 días</option>
              <option value="30days">Últimos 30 días</option>
              <option value="90days">Últimos 90 días</option>
              <option value="12months">Últimos 12 meses</option>
              <option value="custom">Personalizado</option>
            </Select>
            <Select 
              value={reportType}
              onChange={(e) => setReportType(e.target.value as ReportType)}
              width="200px"
            >
              <option value="all">Todos los reportes</option>
              <option value="sales">Ventas</option>
              <option value="properties">Propiedades</option>
              <option value="users">Usuarios</option>
              <option value="financial">Financiero</option>
            </Select>
            <Button 
              leftIcon={<FiFilter />} 
              colorScheme="blue"
              onClick={handleGenerateReport}
            >
              Generar Reporte
            </Button>
          </HStack>
        </HStack>

        {/* Resumen de métricas */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mt={6}>
          <Card>
            <CardHeader pb={0}>
              <HStack>
                <Icon as={FiDollarSign} color="blue.500" boxSize={6} />
                <Text fontWeight="medium">Ventas Totales</Text>
              </HStack>
            </CardHeader>
            <CardBody>
              <Stat>
                <StatNumber>${reportData.totalSales.value.toLocaleString()}</StatNumber>
                <StatHelpText>
                  <StatArrow type={reportData.totalSales.isIncrease ? 'increase' : 'decrease'} />
                  {reportData.totalSales.change}% respecto al período anterior
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardHeader pb={0}>
              <HStack>
                <Icon as={FiHome} color="green.500" boxSize={6} />
                <Text fontWeight="medium">Nuevas Propiedades</Text>
              </HStack>
            </CardHeader>
            <CardBody>
              <Stat>
                <StatNumber>{reportData.newProperties.value}</StatNumber>
                <StatHelpText>
                  <StatArrow type={reportData.newProperties.isIncrease ? 'increase' : 'decrease'} />
                  {reportData.newProperties.change}% respecto al período anterior
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardHeader pb={0}>
              <HStack>
                <Icon as={FiUsers} color="purple.500" boxSize={6} />
                <Text fontWeight="medium">Nuevos Usuarios</Text>
              </HStack>
            </CardHeader>
            <CardBody>
              <Stat>
                <StatNumber>{reportData.newUsers.value}</StatNumber>
                <StatHelpText>
                  <StatArrow type={reportData.newUsers.isIncrease ? 'increase' : 'decrease'} />
                  {reportData.newUsers.change}% respecto al período anterior
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardHeader pb={0}>
              <HStack>
                <Icon as={FiTrendingUp} color="orange.500" boxSize={6} />
                <Text fontWeight="medium">Ingresos</Text>
              </HStack>
            </CardHeader>
            <CardBody>
              <Stat>
                <StatNumber>${reportData.revenue.value.toLocaleString()}</StatNumber>
                <StatHelpText>
                  <StatArrow type={reportData.revenue.isIncrease ? 'increase' : 'decrease'} />
                  {reportData.revenue.change}% respecto al período anterior
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Gráficos y tablas */}
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6} mt={6}>
          {/* Tabla de propiedades destacadas */}
          <Card>
            <CardHeader>
              <Heading size="md">Propiedades más vistas</Heading>
            </CardHeader>
            <CardBody>
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Propiedad</Th>
                    <Th isNumeric>Precio</Th>
                    <Th isNumeric>Vistas</Th>
                    <Th isNumeric>Interesados</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {reportData.topProperties.map((prop) => (
                    <Tr key={prop.id}>
                      <Td>
                        <Text fontWeight="medium">{prop.name}</Text>
                        <Text fontSize="sm" color="gray.500">{prop.location}</Text>
                      </Td>
                      <Td isNumeric>${prop.price.toLocaleString()}</Td>
                      <Td isNumeric>{prop.views.toLocaleString()}</Td>
                      <Td isNumeric>{prop.inquiries}</Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </CardBody>
            <CardFooter>
              <Button 
                leftIcon={<FiDownload />} 
                variant="outline" 
                size="sm"
                onClick={() => handleDownloadReport('excel')}
              >
                Exportar a Excel
              </Button>
            </CardFooter>
          </Card>

          {/* Actividad de usuarios */}
          <Card>
            <CardHeader>
              <Heading size="md">Actividad de Usuarios</Heading>
            </CardHeader>
            <CardBody>
              <Table variant="simple">
                <Thead>
                  <Tr>
                    <Th>Usuario</Th>
                    <Th>Rol</Th>
                    <Th isNumeric>Acciones</Th>
                    <Th>Última Actividad</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  {reportData.userActivity.map((user) => (
                    <Tr key={user.id}>
                      <Td fontWeight="medium">{user.name}</Td>
                      <Td><Badge colorScheme={user.role === 'Administrador' ? 'blue' : user.role === 'Agente' ? 'green' : 'gray'}>{user.role}</Badge></Td>
                      <Td isNumeric>{user.actions}</Td>
                      <Td>{user.lastActive}</Td>
                    </Tr>
                  ))}
                </Tbody>
              </Table>
            </CardBody>
            <CardFooter>
              <Button 
                leftIcon={<FiDownload />} 
                variant="outline" 
                size="sm"
                onClick={() => handleDownloadReport('pdf')}
              >
                Exportar a PDF
              </Button>
            </CardFooter>
          </Card>
        </SimpleGrid>

        {/* Gráfico de tendencias */}
        <Card>
          <CardHeader>
            <Heading size="md">Tendencias de Ventas</Heading>
          </CardHeader>
          <CardBody>
            <Box h="300px" bg="gray.50" borderRadius="md" p={4} display="flex" alignItems="center" justifyContent="center">
              <VStack>
                <Icon as={FiBarChart2} boxSize={12} color="gray.300" />
                <Text color="gray.500">Gráfico de tendencias de ventas</Text>
                <Text fontSize="sm" color="gray.400">Los datos del gráfico se cargarán al generar el reporte</Text>
              </VStack>
            </Box>
          </CardBody>
          <CardFooter justify="space-between">
            <Text fontSize="sm" color="gray.500">Selecciona un rango de fechas para ver los datos</Text>
            <Button 
              leftIcon={<FiDownload />} 
              colorScheme="blue"
              onClick={() => handleDownloadReport('pdf')}
            >
              Exportar Reporte Completo
            </Button>
          </CardFooter>
        </Card>
      </VStack>

      {/* Modal de generación de reporte */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Generando Reporte</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} py={4}>
              <Text>Se está generando el reporte con los siguientes parámetros:</Text>
              <Box width="100%" p={4} bg="gray.50" borderRadius="md">
                <Text><strong>Tipo de reporte:</strong> {reportType === 'all' ? 'Todos los reportes' : reportType}</Text>
                <Text><strong>Rango de fechas:</strong> 
                  {timeRange === '7days' ? 'Últimos 7 días' : 
                   timeRange === '30days' ? 'Últimos 30 días' :
                   timeRange === '90days' ? 'Últimos 90 días' :
                   timeRange === '12months' ? 'Últimos 12 meses' : 'Personalizado'}
                </Text>
              </Box>
              <Progress size="sm" isIndeterminate width="100%" />
              <Text fontSize="sm" color="gray.500">Por favor espera mientras se genera el reporte...</Text>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={onClose}>
              Cerrar
            </Button>
            <Button variant="ghost" onClick={() => handleDownloadReport('pdf')}>
              <FiDownload style={{ marginRight: '8px' }} />
              Descargar PDF
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default Reports;
