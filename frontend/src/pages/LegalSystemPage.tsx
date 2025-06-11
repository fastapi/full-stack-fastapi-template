import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Center,
  VStack
} from '@chakra-ui/react';

import LegalSystem from '../components/Legal/LegalSystem';

interface User {
  id: string;
  email: string;
  role: string;
  name: string;
}

const LegalSystemPage: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasAccess, setHasAccess] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    checkUserAccess();
  }, []);

  const checkUserAccess = async () => {
    try {
      // TODO: Get user from auth context or API
      const mockUser: User = {
        id: '1',
        email: 'admin@genius-industries.com',
        role: 'ceo', // ceo, manager, agent
        name: 'Administrador Sistema'
      };

      // Check if user has access to legal system
      const allowedRoles = ['ceo', 'manager', 'agent'];
      const userHasAccess = allowedRoles.includes(mockUser.role);

      if (!userHasAccess) {
        navigate('/unauthorized');
        return;
      }

      setUser(mockUser);
      setHasAccess(true);
    } catch (error) {
      console.error('Error checking user access:', error);
      navigate('/login');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Center minH="100vh" bg="gray.50">
        <VStack spacing={4}>
          <Spinner size="xl" color="black" thickness="4px" />
          <Box textAlign="center">
            <Box
              w={12}
              h={12}
              bg="black"
              color="white"
              display="flex"
              alignItems="center"
              justifyContent="center"
              mx="auto"
              mb={2}
              fontWeight="bold"
              fontSize="sm"
              borderRadius="md"
            >
              GI
            </Box>
            <Box color="black" fontWeight="semibold">
              Cargando Sistema Legal...
            </Box>
            <Box color="gray.600" fontSize="sm">
              GENIUS INDUSTRIES
            </Box>
          </Box>
        </VStack>
      </Center>
    );
  }

  if (!hasAccess) {
    return (
      <Center minH="100vh" bg="gray.50">
        <Alert
          status="error"
          variant="subtle"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          textAlign="center"
          height="200px"
          borderRadius="lg"
          maxW="md"
        >
          <AlertIcon boxSize="40px" mr={0} />
          <AlertTitle mt={4} mb={1} fontSize="lg">
            Acceso Denegado
          </AlertTitle>
          <AlertDescription maxWidth="sm">
            No tienes permisos para acceder al Sistema Legal de GENIUS INDUSTRIES.
            Contacta al administrador si necesitas acceso.
          </AlertDescription>
        </Alert>
      </Center>
    );
  }

  return (
    <Box minH="100vh" bg="gray.50">
      <LegalSystem />
    </Box>
  );
};

export default LegalSystemPage; 