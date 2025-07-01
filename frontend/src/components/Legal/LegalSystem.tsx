import React, { useState } from 'react';
import {
  Box,
  Button,
  Flex,
  Icon,
  VStack,
  Heading,
  Text
} from '@chakra-ui/react';
import {
  FiHome,
  FiFileText,
  FiEdit3,
  FiList,
  FiBarChart2,
  FiSettings
} from 'react-icons/fi';

import LegalDashboard from './LegalDashboard';
import DocumentGenerator from './DocumentGenerator';
import TemplateManager from './TemplateManager';
import DocumentsList from './DocumentsList';

const LegalReports: React.FC = () => {
  return (
    <Box maxW="7xl" mx="auto" px={6}>
      <Box textAlign="center">
        <Icon as={FiBarChart2} w={16} h={16} color="gray.400" mb={4} />
        <Heading size="lg" color="black" mb={2}>
          Reportes y Estadísticas
        </Heading>
        <Text color="gray.600">
          Módulo de reportes en desarrollo
        </Text>
        <Text fontSize="sm" color="gray.500" mt={2}>
          Aquí se mostrarán análisis detallados de documentos generados, 
          tendencias de uso de templates y métricas de cumplimiento legal.
        </Text>
      </Box>
    </Box>
  );
};

const tabs = [
  {
    label: 'Dashboard',
    icon: FiHome,
    component: <LegalDashboard />,
    description: 'Vista general del sistema legal'
  },
  {
    label: 'Generar Documento',
    icon: FiFileText,
    component: <DocumentGenerator />,
    description: 'Crear nuevos documentos legales'
  },
  {
    label: 'Gestionar Templates',
    icon: FiEdit3,
    component: <TemplateManager />,
    description: 'Administrar plantillas de documentos'
  },
  {
    label: 'Lista de Documentos',
    icon: FiList,
    component: <DocumentsList />,
    description: 'Ver todos los documentos generados'
  },
  {
    label: 'Reportes',
    icon: FiBarChart2,
    component: <LegalReports />,
    description: 'Análisis y estadísticas legales'
  }
];

const LegalSystem: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);

  // Theme colors
  const activeBg = "black";
  const activeColor = "white";
  const inactiveColor = "gray.600";

  return (
    <Box minH="100vh" bg="gray.50">
      <Box maxW="7xl" mx="auto" px={6}>
        {/* Header */}
        <Box mb={6}>
          <Flex align="center" mb={4}>
            <Box 
              w={16} 
              h={16} 
              bg="black" 
              color="white" 
              display="flex" 
              alignItems="center" 
              justifyContent="center" 
              mr={4}
              fontWeight="bold"
              fontSize="lg"
              borderRadius="md"
            >
              GI
            </Box>
            <VStack align="start" spacing={0}>
              <Heading size="xl" color="black">
                Sistema Legal GENIUS INDUSTRIES
              </Heading>
              <Text color="gray.600" fontSize="md">
                Gestión completa de documentos legales con branding corporativo
              </Text>
            </VStack>
          </Flex>
          <Box height="2px" bg="black" width="100%" />
        </Box>

        {/* Manual Tabs */}
        <Flex mb={6} wrap="wrap" gap={2}>
          {tabs.map((tab, index) => (
            <Button
              key={index}
              leftIcon={<Icon as={tab.icon} />}
              onClick={() => setActiveTab(index)}
              bg={activeTab === index ? activeBg : "white"}
              color={activeTab === index ? activeColor : inactiveColor}
              border={"1px solid"}
              borderColor={activeTab === index ? "black" : "gray.200"}
              fontWeight="semibold"
              px={6}
              py={3}
              borderRadius="md"
              _hover={{ bg: activeTab === index ? activeBg : "gray.100" }}
              transition="all 0.2s"
            >
              {tab.label}
            </Button>
          ))}
        </Flex>

        {/* Tab Content */}
        <Box
          bg="white"
          borderRadius="lg"
          shadow="sm"
          border="1px solid"
          borderColor="gray.200"
          minH="600px"
        >
          {tabs[activeTab].component}
        </Box>

        {/* Footer */}
        <Box 
          mt={8} 
          p={6} 
          bg="black" 
          color="white" 
          borderRadius="lg"
          textAlign="center"
        >
          <Flex justify="center" align="center" mb={2}>
            <Box 
              w={8} 
              h={8} 
              bg="white" 
              color="black" 
              display="flex" 
              alignItems="center" 
              justifyContent="center" 
              mr={3}
              fontWeight="bold"
              fontSize="sm"
              borderRadius="md"
            >
              GI
            </Box>
            <Text fontWeight="bold" fontSize="lg">
              GENIUS INDUSTRIES
            </Text>
          </Flex>
          <Text fontSize="sm" color="gray.300">
            Sistema Legal Corporativo | Todos los documentos incluyen branding oficial
          </Text>
          <Text fontSize="xs" color="gray.400" mt={2}>
            © 2024 GENIUS INDUSTRIES. Todos los derechos reservados.
          </Text>
        </Box>
      </Box>
    </Box>
  );
};

export default LegalSystem; 
