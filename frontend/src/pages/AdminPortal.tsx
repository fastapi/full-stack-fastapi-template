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
import { FaUsers, FaHome, FaMoneyBillWave, FaCog } from 'react-icons/fa';
import { useQuery } from '@tanstack/react-query';
import { nhost } from '../lib/nhost';

export const AdminPortal: React.FC = () => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Fetch admin stats
  const { data: stats } = useQuery({
    queryKey: ['adminStats'],
    queryFn: async () => {
      const { data, error } = await nhost.graphql.request(`
        query GetAdminStats {
          users_aggregate {
            aggregate {
              count
            }
          }
          properties_aggregate {
            aggregate {
              count
            }
          }
          loans_aggregate {
            aggregate {
              count
            }
          }
          transactions_aggregate {
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
          <Heading size="lg" mb={2}>Portal Administrador</Heading>
          <Text color="gray.600">
            Gestión global del sistema y configuración
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
              <Icon as={FaUsers} boxSize={6} color="blue.500" />
              <Box>
                <StatLabel>Usuarios</StatLabel>
                <StatNumber>{stats?.users_aggregate.aggregate.count || 0}</StatNumber>
                <StatHelpText>Total registrados</StatHelpText>
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
              <Icon as={FaHome} boxSize={6} color="green.500" />
              <Box>
                <StatLabel>Propiedades</StatLabel>
                <StatNumber>{stats?.properties_aggregate.aggregate.count || 0}</StatNumber>
                <StatHelpText>En el sistema</StatHelpText>
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
              <Icon as={FaMoneyBillWave} boxSize={6} color="purple.500" />
              <Box>
                <StatLabel>Préstamos</StatLabel>
                <StatNumber>{stats?.loans_aggregate.aggregate.count || 0}</StatNumber>
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
              <Icon as={FaCog} boxSize={6} color="orange.500" />
              <Box>
                <StatLabel>Transacciones</StatLabel>
                <StatNumber>{stats?.transactions_aggregate.aggregate.count || 0}</StatNumber>
                <StatHelpText>Totales</StatHelpText>
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
                  <Icon as={FaUsers} />
                  <Text>Usuarios</Text>
                </HStack>
              </Tab>
              <Tab>
                <HStack>
                  <Icon as={FaHome} />
                  <Text>Propiedades</Text>
                </HStack>
              </Tab>
              <Tab>
                <HStack>
                  <Icon as={FaMoneyBillWave} />
                  <Text>Créditos</Text>
                </HStack>
              </Tab>
              <Tab>
                <HStack>
                  <Icon as={FaCog} />
                  <Text>Configuración</Text>
                </HStack>
              </Tab>
            </TabList>

            <TabPanels>
              <TabPanel>
                {/* UserManagement component will be added here */}
                <Text>Gestión de Usuarios</Text>
              </TabPanel>
              <TabPanel>
                {/* PropertyManagement component will be added here */}
                <Text>Gestión de Propiedades</Text>
              </TabPanel>
              <TabPanel>
                {/* CreditManagement component will be added here */}
                <Text>Gestión de Créditos</Text>
              </TabPanel>
              <TabPanel>
                {/* SystemConfiguration component will be added here */}
                <Text>Configuración del Sistema</Text>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </Box>
      </VStack>
    </Container>
  );
}; 