import React, { useState } from 'react';
import {
  Box,
  Container,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Icon,
  Flex,
  VStack,
  Heading,
  Text,
  Divider,
  useColorModeValue
} from '@chakra-ui/react';
import {
  FiHome,
  FiFileText,
  FiEdit3,
  FiList,
  FiBarChart3,
  FiSettings
} from 'react-icons/fi';

import LegalDashboard from './LegalDashboard';
import DocumentGenerator from './DocumentGenerator';
import TemplateManager from './TemplateManager';
import DocumentsList from './DocumentsList';

const LegalSystem: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);

  // Theme colors
  const tabBg = useColorModeValue('white', 'gray.800');
  const activeBg = useColorModeValue('black', 'white');
  const activeColor = useColorModeValue('white', 'black');
  const inactiveColor = useColorModeValue('gray.600', 'gray.400');

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
      icon: FiBarChart3,
      component: <LegalReports />,
      description: 'Análisis y estadísticas legales'
    }
  ];

  return (
    <Box minH="100vh" bg="gray.50">
      <Container maxW="8xl" py={4}>
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
          <Divider borderColor="black" borderWidth="2px" />
        </Box>

        {/* Navigation Tabs */}
        <Tabs 
          index={activeTab} 
          onChange={setActiveTab}
          variant="enclosed"
          colorScheme="black"
        >
          <TabList 
            bg={tabBg}
            borderRadius="lg"
            p={2}
            mb={6}
            overflowX="auto"
            css={{
              '&::-webkit-scrollbar': {
                height: '4px',
              },
              '&::-webkit-scrollbar-track': {
                background: 'transparent',
              },
              '&::-webkit-scrollbar-thumb': {
                background: '#E2E8F0',
                borderRadius: '2px',
              },
            }}
          >
            {tabs.map((tab, index) => (
              <Tab
                key={index}
                _selected={{
                  bg: activeBg,
                  color: activeColor,
                  borderColor: 'black',
                  transform: 'translateY(-2px)',
                  transition: 'all 0.2s'
                }}
                _hover={{
                  bg: activeTab === index ? activeBg : 'gray.100',
                  transform: 'translateY(-1px)',
                  transition: 'all 0.2s'
                }}
                color={activeTab === index ? activeColor : inactiveColor}
                fontWeight="semibold"
                px={6}
                py={3}
                mr={2}
                borderRadius="md"
                border="1px solid"
                borderColor={activeTab === index ? 'black' : 'gray.200'}
                whiteSpace="nowrap"
              >
                <Flex align="center">
                  <Icon 
                    as={tab.icon} 
                    w={5} 
                    h={5} 
                    mr={2}
                    color={activeTab === index ? activeColor : inactiveColor}
                  />
                  {tab.label}
                </Flex>
              </Tab>
            ))}
          </TabList>

          {/* Tab Panels */}
          <TabPanels>
            {tabs.map((tab, index) => (
              <TabPanel key={index} p={0}>
                <Box
                  bg="white"
                  borderRadius="lg"
                  shadow="sm"
                  border="1px solid"
                  borderColor="gray.200"
                  minH="600px"
                >
                  {tab.component}
                </Box>
              </TabPanel>
            ))}
          </TabPanels>
        </Tabs>

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
      </Container>
    </Box>
  );
};

// Placeholder component for Reports
const LegalReports: React.FC = () => {
  return (
    <Container maxW="7xl" py={8}>
      <Box textAlign="center">
        <Icon as={FiBarChart3} w={16} h={16} color="gray.400" mb={4} />
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
    </Container>
  );
};

export default LegalSystem; 