import React, { useState, useEffect } from 'react';
import {
  Box,
  
  Heading,
  Text,
  Grid,
  Card,
  CardBody,
  Button,
  Icon,
  Flex,
  Badge,
  HStack,
  VStack
} from '@chakra-ui/react';
import {
  FiFileText,
  FiEdit3,
  FiUsers,
  FiShield,
  FiTrendingUp,
  FiPlus,
  FiEye,
  FiDownload
} from 'react-icons/fi';

interface LegalStats {
  totalDocuments: number;
  templatesActive: number;
  documentsThisMonth: number;
  pendingSignatures: number;
}

const LegalDashboard: React.FC = () => {
  const [stats, setStats] = useState<LegalStats>({
    totalDocuments: 0,
    templatesActive: 0,
    documentsThisMonth: 0,
    pendingSignatures: 0
  });

  const [recentDocuments, setRecentDocuments] = useState([]);

  // Corporate theme colors
  const bgColor = "white";
  const borderColor = "gray.200";
  const accentColor = 'black';
  
  useEffect(() => {
    // TODO: Fetch real data from API
    setStats({
      totalDocuments: 47,
      templatesActive: 8,
      documentsThisMonth: 12,
      pendingSignatures: 3
    });
  }, []);

  const quickActions = [
    {
      title: 'Nuevo Contrato',
      description: 'Generar documento legal',
      icon: FiPlus,
      action: () => {/* Navigate to document generator */},
      color: 'black'
    },
    {
      title: 'Gestionar Templates',
      description: 'Administrar plantillas',
      icon: FiEdit3,
      action: () => {/* Navigate to template manager */},
      color: 'gray.600'
    },
    {
      title: 'Ver Documentos',
      description: 'Lista de documentos',
      icon: FiEye,
      action: () => {/* Navigate to documents list */},
      color: 'gray.600'
    },
    {
      title: 'Reportes',
      description: 'Análisis y estadísticas',
      icon: FiTrendingUp,
      action: () => {/* Navigate to reports */},
      color: 'gray.600'
    }
  ];

  return (
    <Box maxW="7xl" mx="auto" px={6}>
      {/* Header */}
      <Box mb={8}>
        <Flex align="center" mb={4}>
          <Box 
            w={12} 
            h={12} 
            bg="black" 
            color="white" 
            display="flex" 
            alignItems="center" 
            justifyContent="center" 
            mr={4}
            fontWeight="bold"
            fontSize="sm"
          >
            GI
          </Box>
          <VStack align="start" spacing={0}>
            <Heading size="lg" color="black">
              Sistema Legal
            </Heading>
            <Text color="gray.600" fontSize="sm">
              GENIUS INDUSTRIES - Gestión de Documentos Legales
            </Text>
          </VStack>
        </Flex>
        <Box height="1px" bg="black" width="100%" />
      </Box>

      {/* Stats Cards */}
      <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(4, 1fr)' }} gap={6} mb={8}>
        <Card 
          bg={bgColor} 
          border="1px solid" 
          borderColor={borderColor}
          _hover={{ 
            borderColor: 'black',
            transform: 'translateY(-2px)',
            transition: 'all 0.2s'
          }}
        >
          <CardBody>
            <Flex align="center" justify="space-between">
              <Box>
                <Text color="gray.600" fontSize="sm">Total Documentos</Text>
                <Text color="black" fontSize="2xl" fontWeight="bold">
                  {stats.totalDocuments}
                </Text>
                <Flex align="center" color="gray.500" fontSize="sm">
                  <Icon as={FiFileText} mr={1} />
                  <Text>Todos los documentos</Text>
                </Flex>
              </Box>
              <Icon as={FiFileText} w={8} h={8} color="black" />
            </Flex>
          </CardBody>
        </Card>

        <Card 
          bg={bgColor} 
          border="1px solid" 
          borderColor={borderColor}
          _hover={{ 
            borderColor: 'black',
            transform: 'translateY(-2px)',
            transition: 'all 0.2s'
          }}
        >
          <CardBody>
            <Flex align="center" justify="space-between">
              <Box>
                <Text color="gray.600" fontSize="sm">Templates Activos</Text>
                <Text color="black" fontSize="2xl" fontWeight="bold">
                  {stats.templatesActive}
                </Text>
                <Flex align="center" color="gray.500" fontSize="sm">
                  <Icon as={FiEdit3} mr={1} />
                  <Text>Plantillas disponibles</Text>
                </Flex>
              </Box>
              <Icon as={FiEdit3} w={8} h={8} color="black" />
            </Flex>
          </CardBody>
        </Card>

        <Card 
          bg={bgColor} 
          border="1px solid" 
          borderColor={borderColor}
          _hover={{ 
            borderColor: 'black',
            transform: 'translateY(-2px)',
            transition: 'all 0.2s'
          }}
        >
          <CardBody>
            <Flex align="center" justify="space-between">
              <Box>
                <Text color="gray.600" fontSize="sm">Este Mes</Text>
                <Text color="black" fontSize="2xl" fontWeight="bold">
                  {stats.documentsThisMonth}
                </Text>
                <Flex align="center" color="green.500" fontSize="sm">
                  <Icon as={FiTrendingUp} mr={1} />
                  <Text>+23% vs mes anterior</Text>
                </Flex>
              </Box>
              <Icon as={FiTrendingUp} w={8} h={8} color="green.500" />
            </Flex>
          </CardBody>
        </Card>

        <Card 
          bg={bgColor} 
          border="1px solid" 
          borderColor={borderColor}
          _hover={{ 
            borderColor: 'black',
            transform: 'translateY(-2px)',
            transition: 'all 0.2s'
          }}
        >
          <CardBody>
            <Flex align="center" justify="space-between">
              <Box>
                <Text color="gray.600" fontSize="sm">Pendientes</Text>
                <Text color="black" fontSize="2xl" fontWeight="bold">
                  {stats.pendingSignatures}
                </Text>
                <Flex align="center" color="orange.500" fontSize="sm">
                  <Icon as={FiUsers} mr={1} />
                  <Text>Firmas pendientes</Text>
                </Flex>
              </Box>
              <Icon as={FiUsers} w={8} h={8} color="orange.500" />
            </Flex>
          </CardBody>
        </Card>
      </Grid>

      {/* Quick Actions */}
      <Box mb={8}>
        <Heading size="md" mb={4} color="black">
          Acciones Rápidas
        </Heading>
        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(4, 1fr)' }} gap={4}>
          {quickActions.map((action, index) => (
            <Card 
              key={index}
              bg={bgColor} 
              border="1px solid" 
              borderColor={borderColor}
              cursor="pointer"
              onClick={action.action}
              _hover={{ 
                borderColor: 'black',
                transform: 'translateY(-2px)',
                transition: 'all 0.2s',
                shadow: 'md'
              }}
            >
              <CardBody p={6}>
                <VStack spacing={3} align="center">
                  <Icon as={action.icon} w={8} h={8} color={action.color} />
                  <Text fontWeight="semibold" color="black" textAlign="center">
                    {action.title}
                  </Text>
                  <Text fontSize="sm" color="gray.600" textAlign="center">
                    {action.description}
                  </Text>
                </VStack>
              </CardBody>
            </Card>
          ))}
        </Grid>
      </Box>

      {/* Recent Documents */}
      <Box>
        <Flex justify="space-between" align="center" mb={4}>
          <Heading size="md" color="black">
            Documentos Recientes
          </Heading>
          <Button 
            variant="outline" 
            borderColor="black" 
            color="black"
            _hover={{ bg: 'black', color: 'white' }}
            size="sm"
          >
            Ver Todos
          </Button>
        </Flex>
        
        <Card bg={bgColor} border="1px solid" borderColor={borderColor}>
          <CardBody>
            <VStack spacing={4} align="stretch">
              {[1, 2, 3].map((item) => (
                <Flex key={item} justify="space-between" align="center" p={4} bg="gray.50" borderRadius="md">
                  <Flex align="center" flex={1}>
                    <Icon as={FiFileText} w={5} h={5} color="black" mr={3} />
                    <VStack align="start" spacing={0}>
                      <Text fontWeight="semibold" color="black">
                        Contrato de Compra-Venta #{`GI-CV-2024-12-000${item}`}
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        Cliente: Juan Pérez | Generado hace 2 días
                      </Text>
                    </VStack>
                  </Flex>
                  <HStack spacing={2}>
                    <Badge colorScheme="green" variant="subtle">
                      Firmado
                    </Badge>
                    <Button size="sm" variant="ghost" color="black">
                      <Icon as={FiEye} />
                    </Button>
                    <Button size="sm" variant="ghost" color="black">
                      <Icon as={FiDownload} />
                    </Button>
                  </HStack>
                </Flex>
              ))}
              
              {/* Empty state */}
              {recentDocuments.length === 0 && (
                <Flex direction="column" align="center" py={8}>
                  <Icon as={FiFileText} w={12} h={12} color="gray.400" mb={4} />
                  <Text color="gray.600" textAlign="center">
                    No hay documentos recientes
                  </Text>
                  <Text fontSize="sm" color="gray.500" textAlign="center">
                    Comienza generando tu primer documento legal
                  </Text>
                  <Button 
                    mt={4}
                    bg="black" 
                    color="white"
                    _hover={{ bg: 'gray.800' }}
                    leftIcon={<Icon as={FiPlus} />}
                  >
                    Crear Documento
                  </Button>
                </Flex>
              )}
            </VStack>
          </CardBody>
        </Card>
      </Box>
    </Box>
  );
};

export default LegalDashboard; 
