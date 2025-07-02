import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Divider,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Badge,
  Flex,
  Heading,
} from '@chakra-ui/react';
import { FiUser, FiLock, FiLogOut, FiShield, FiMail, FiPhone, FiCalendar } from 'react-icons/fi';
import useAuth from '@/hooks/useAuth';
import UserInformation from './UserInformation';
import ChangePassword from './ChangePassword';
import Appearance from './Appearance';

interface ProfileSettingsProps {
  onClose?: () => void;
}

const ProfileSettings: React.FC<ProfileSettingsProps> = ({ onClose }) => {
  const [activeSection, setActiveSection] = useState<'profile' | 'password' | 'appearance'>('profile');
  const { user, logout } = useAuth();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const handleLogout = async () => {
    try {
      await logout();
      if (onClose) onClose();
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'profile':
        return <UserInformation />;
      case 'password':
        return <ChangePassword />;
      case 'appearance':
        return <Appearance />;
      default:
        return <UserInformation />;
    }
  };

  const getRoleColor = (role: string) => {
    const roleColors: Record<string, string> = {
      'ceo': 'purple',
      'manager': 'blue',
      'supervisor': 'green',
      'hr': 'orange',
      'agent': 'teal',
      'support': 'cyan',
      'client': 'gray',
    };
    return roleColors[role?.toLowerCase()] || 'gray';
  };

  return (
    <Box maxW="5xl" mx="auto" p={6}>
      <VStack align="stretch" spacing={6}>
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>
            Configuración de Perfil
          </Heading>
          <Text color="gray.600">
            Gestiona tu información personal y configuraciones de cuenta
          </Text>
        </Box>

        {/* User Info Alert */}
        <Alert status="info" borderRadius="lg">
          <AlertIcon />
          <Box flex="1">
            <AlertTitle fontSize="sm">Información Importante:</AlertTitle>
            <AlertDescription fontSize="sm">
              Tu rol y cargo no pueden ser modificados desde aquí. Para cambios de rol, contacta al administrador del sistema.
            </AlertDescription>
          </Box>
        </Alert>

        {/* Current User Info */}
        <Box bg={bgColor} p={4} borderRadius="lg" border="1px" borderColor={borderColor}>
          <Text fontSize="sm" color="gray.600" mb={2}>Usuario Actual</Text>
          <Flex align="center" justify="space-between">
            <VStack align="start" spacing={1}>
              <HStack>
                <FiUser />
                <Text fontWeight="medium">{user?.full_name || 'Usuario'}</Text>
              </HStack>
              <HStack>
                <FiMail />
                <Text fontSize="sm" color="gray.600">{user?.email}</Text>
              </HStack>
              {user?.phone && (
                <HStack>
                  <FiPhone />
                  <Text fontSize="sm" color="gray.600">{user.phone}</Text>
                </HStack>
              )}
              <HStack>
                <FiCalendar />
                <Text fontSize="sm" color="gray.600">
                  Miembro desde {new Date(user?.created_at || '').toLocaleDateString('es-CO')}
                </Text>
              </HStack>
            </VStack>
            <VStack align="end" spacing={1}>
              <Badge colorScheme={getRoleColor(user?.role || '')} variant="solid">
                <HStack spacing={1}>
                  <FiShield size={12} />
                  <Text>{user?.role?.toUpperCase()}</Text>
                </HStack>
              </Badge>
              {user?.is_superuser && (
                <Badge colorScheme="red" variant="outline" size="sm">
                  SUPERUSER
                </Badge>
              )}
            </VStack>
          </Flex>
        </Box>

        <Flex direction={{ base: 'column', md: 'row' }} gap={6}>
          {/* Navigation Menu */}
          <Box minW="200px">
            <VStack align="stretch" spacing={2}>
              <Button
                variant={activeSection === 'profile' ? 'solid' : 'ghost'}
                justifyContent="start"
                leftIcon={<FiUser />}
                onClick={() => setActiveSection('profile')}
                size="sm"
              >
                Información Personal
              </Button>
              <Button
                variant={activeSection === 'password' ? 'solid' : 'ghost'}
                justifyContent="start"
                leftIcon={<FiLock />}
                onClick={() => setActiveSection('password')}
                size="sm"
              >
                Cambiar Contraseña
              </Button>
              <Button
                variant={activeSection === 'appearance' ? 'solid' : 'ghost'}
                justifyContent="start"
                leftIcon={<FiShield />}
                onClick={() => setActiveSection('appearance')}
                size="sm"
              >
                Apariencia
              </Button>
            </VStack>
          </Box>

          {/* Content Area */}
          <Box flex="1" bg={bgColor} borderRadius="lg" border="1px" borderColor={borderColor}>
            {renderContent()}
          </Box>
        </Flex>

        {/* Logout Section */}
        <Divider />
        <Box>
          <VStack align="start" spacing={3}>
            <Text fontWeight="medium" color="gray.700">
              Sesión y Seguridad
            </Text>
            <Text fontSize="sm" color="gray.600">
              Cerrar sesión te desconectará de la plataforma de forma segura.
            </Text>
            <Button
              colorScheme="red"
              variant="outline"
              leftIcon={<FiLogOut />}
              onClick={handleLogout}
              size="sm"
            >
              Cerrar Sesión
            </Button>
          </VStack>
        </Box>

        {/* Close Button */}
        {onClose && (
          <Box textAlign="center">
            <Button variant="ghost" onClick={onClose}>
              Cerrar Configuración
            </Button>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default ProfileSettings; 