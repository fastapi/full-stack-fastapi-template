import React from 'react';
import {
  Box,
  Container,
  VStack,
  Heading,
  Text,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useColorModeValue,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  Icon,
  HStack,
} from '@chakra-ui/react';
import { FaHome, FaUsers, FaCalendarAlt, FaChartLine } from 'react-icons/fa';
import { useQuery } from '@tanstack/react-query';
import { nhost } from '../lib/nhost';
import { PropertyManagement } from '../components/agent/PropertyManagement';
import { ClientManagement } from '../components/agent/ClientManagement';
import { VisitManagement } from '../components/agent/VisitManagement';

export const AgentPortal: React.FC = () => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Fetch agent stats
  const { data: stats } = useQuery({
    queryKey: ['agentStats'],
    queryFn: async () => {
      const { data, error } = await nhost.graphql.request(`
        query GetAgentStats {
          properties_aggregate(where: {agent_id: {_eq: $agentId}}) {
            aggregate {
              count
            }
          }
          clients_aggregate(where: {agent_id: {_eq: $agentId}}) {
            aggregate {
              count
            }
          }
          visits_aggregate(where: {agent_id: {_eq: $agentId}}) {
            aggregate {
              count
            }
          }
          properties_aggregate(where: {agent_id: {_eq: $agentId}, status: {_eq: "sold"}}) {
            aggregate {
              count
            }
          }
        }
      `);
      if (error) throw error;
      return data;
    },
  });

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={2}>Portal del Agente</Heading>
          <Text color="gray.600">
            Gestiona tus propiedades, clientes y visitas desde un solo lugar
          </Text>
        </Box>

        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Stat
            px={4}
            py={5}
            bg={bgColor}
            shadow="base"
            rounded="lg"
            borderWidth="1px"
            borderColor={borderColor}
          >
            <HStack>
              <Icon as={FaHome} boxSize={6} color="blue.500" />
              <Box>
                <StatLabel>Propiedades</StatLabel>
                <StatNumber>{stats?.properties_aggregate.aggregate.count || 0}</StatNumber>
                <StatHelpText>Activas</StatHelpText>
              </Box>
            </HStack>
          </Stat>

          <Stat
            px={4}
            py={5}
            bg={bgColor}
            shadow="base"
            rounded="lg"
            borderWidth="1px"
            borderColor={borderColor}
          >
            <HStack>
              <Icon as={FaUsers} boxSize={6} color="green.500" />
              <Box>
                <StatLabel>Clientes</StatLabel>
                <StatNumber>{stats?.clients_aggregate.aggregate.count || 0}</StatNumber>
                <StatHelpText>Activos</StatHelpText>
              </Box>
            </HStack>
          </Stat>

          <Stat
            px={4}
            py={5}
            bg={bgColor}
            shadow="base"
            rounded="lg"
            borderWidth="1px"
            borderColor={borderColor}
          >
            <HStack>
              <Icon as={FaCalendarAlt} boxSize={6} color="purple.500" />
              <Box>
                <StatLabel>Visitas</StatLabel>
                <StatNumber>{stats?.visits_aggregate.aggregate.count || 0}</StatNumber>
                <StatHelpText>Programadas</StatHelpText>
              </Box>
            </HStack>
          </Stat>

          <Stat
            px={4}
            py={5}
            bg={bgColor}
            shadow="base"
            rounded="lg"
            borderWidth="1px"
            borderColor={borderColor}
          >
            <HStack>
              <Icon as={FaChartLine} boxSize={6} color="orange.500" />
              <Box>
                <StatLabel>Ventas</StatLabel>
                <StatNumber>{stats?.properties_aggregate.aggregate.count || 0}</StatNumber>
                <StatHelpText>Completadas</StatHelpText>
              </Box>
            </HStack>
          </Stat>
        </SimpleGrid>

        <Box
          bg={bgColor}
          shadow="base"
          rounded="lg"
          borderWidth="1px"
          borderColor={borderColor}
        >
          <Tabs variant="enclosed" colorScheme="black">
            <TabList>
              <Tab>
                <HStack>
                  <Icon as={FaHome} />
                  <Text>Propiedades</Text>
                </HStack>
              </Tab>
              <Tab>
                <HStack>
                  <Icon as={FaUsers} />
                  <Text>Clientes</Text>
                </HStack>
              </Tab>
              <Tab>
                <HStack>
                  <Icon as={FaCalendarAlt} />
                  <Text>Visitas</Text>
                </HStack>
              </Tab>
            </TabList>

            <TabPanels>
              <TabPanel>
                <PropertyManagement />
              </TabPanel>
              <TabPanel>
                <ClientManagement />
              </TabPanel>
              <TabPanel>
                <VisitManagement />
              </TabPanel>
            </TabPanels>
          </Tabs>
        </Box>
      </VStack>
    </Container>
  );
}; 