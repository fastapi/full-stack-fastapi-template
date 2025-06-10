import React from 'react';
import {
  Box,
  Container,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
  useColorModeValue,
} from '@chakra-ui/react';
import { ProfileSection } from '../../components/client/ProfileSection';
import { FavoritesSection } from '../../components/client/FavoritesSection';
import { VisitsSection } from '../../components/client/VisitsSection';

export const ClientPortal: React.FC = () => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const tabBgColor = useColorModeValue('white', 'gray.800');

  return (
    <Box minH="100vh" bg={bgColor} py={8}>
      <Container maxW="container.xl">
        <Tabs variant="enclosed" colorScheme="black">
          <TabList bg={tabBgColor} borderRadius="lg" p={2} shadow="sm">
            <Tab>Perfil</Tab>
            <Tab>Favoritos</Tab>
            <Tab>Visitas</Tab>
          </TabList>

          <TabPanels>
            <TabPanel>
              <ProfileSection />
            </TabPanel>
            <TabPanel>
              <FavoritesSection />
            </TabPanel>
            <TabPanel>
              <VisitsSection />
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Container>
    </Box>
  );
}; 