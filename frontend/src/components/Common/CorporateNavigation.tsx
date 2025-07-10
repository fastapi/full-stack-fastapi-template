import React from 'react';
import {
  Box,
  
  Flex,
  HStack,
  Button,
  Icon,
  Text,
  useColorModeValue
} from '@chakra-ui/react';
import { Link as RouterLink, useLocation } from '@tanstack/react-router';
import {
  FiHome,
  FiUsers,
  FiMail,
  FiShield
} from 'react-icons/fi';

const CorporateNavigation: React.FC = () => {
  const location = useLocation();
  const bg = "white";
  const borderColor = "gray.200";

  const navItems = [
    {
      label: 'Inicio',
      path: '/',
      icon: FiHome
    },
    {
      label: 'Conócenos',
      path: '/about',
      icon: FiUsers
    },
    {
      label: 'Proyectos',
      path: '/projects',
      icon: FiHome
    },
    {
      label: 'Contacto',
      path: '/contact',
      icon: FiMail
    },
    {
      label: 'Sistema Legal',
      path: '/legal',
      icon: FiShield
    }
  ];

  return (
    <Box
      position="sticky"
      top={0}
      zIndex={100}
      bg={bg}
      borderBottom="1px solid"
      borderColor={borderColor}
      shadow="sm"
    >
      <Box maxW="7xl" mx="auto" px={6}>
        <Flex align="center" justify="space-between" py={4}>
          {/* Logo */}
          <Flex align="center">
            <Box
              w={10}
              h={10}
              bg="black"
              color="white"
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
            <Text fontWeight="bold" fontSize="lg" color="text">
              Genius Industries
            </Text>
          </Flex>

          {/* Navigation */}
          <HStack spacing={1}>
            {navItems.map((item) => (
              <Button
                key={item.path}
                as={RouterLink}
                to={item.path}
                variant="ghost"
                size="sm"
                color={location.pathname === item.path ? 'black' : 'gray.600'}
                bg={location.pathname === item.path ? 'gray.100' : 'transparent'}
                _hover={{
                  bg: 'gray.100',
                  color: 'black'
                }}
                leftIcon={<Icon as={item.icon} />}
                fontWeight={location.pathname === item.path ? 'bold' : 'normal'}
              >
                {item.label}
              </Button>
            ))}
          </HStack>
        </Flex>
      </Box>
    </Box>
  );
};

export default CorporateNavigation; 
