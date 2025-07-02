import { 
  SignIn, 
  SignUp, 
  UserButton, 
  SignedIn, 
  SignedOut,
  useUser,
  useAuth 
} from '@clerk/clerk-react'
import { Box, Button, Flex, Text, VStack, HStack } from '@chakra-ui/react'
import { useNavigate } from '@tanstack/react-router'
import { useEffect } from 'react'

// Función para obtener la URL de redirección basada en el rol
function getRedirectUrlByRole(role?: string): string {
  switch (role) {
    case 'CEO':
    case 'MANAGER':
    case 'SUPERVISOR':
    case 'HR':
    case 'AGENT':
    case 'SUPPORT':
      return '/admin'
    case 'CLIENT':
      return '/client-dashboard'
    default:
      return '/client-dashboard' // Por defecto redirige a client dashboard
  }
}

interface AuthWrapperProps {
  children: React.ReactNode
  requiredRole?: string[]
}

export function AuthWrapper({ children, requiredRole }: AuthWrapperProps) {
  const { user, isLoaded } = useUser()
  const navigate = useNavigate()

  useEffect(() => {
    if (isLoaded && user && requiredRole) {
      const userRole = user.publicMetadata?.role as string
      if (!requiredRole.includes(userRole)) {
        navigate({ to: '/unauthorized' })
      }
    }
  }, [isLoaded, user, requiredRole, navigate])

  if (!isLoaded) {
    return (
      <Flex minH="100vh" align="center" justify="center" bg="bg">
        <VStack spacing={4}>
          <Box 
            w={12} 
            h={12} 
            borderRadius="full" 
            border="4px solid"
            borderColor="blue.500"
            borderTopColor="transparent"
            animation="spin 1s linear infinite"
          />
          <Text color="text.muted">Cargando...</Text>
        </VStack>
      </Flex>
    )
  }

  return (
    <>
      <SignedIn>
        {children}
      </SignedIn>
      <SignedOut>
        <SignInPage />
      </SignedOut>
    </>
  )
}

export function SignInPage() {
  return (
    <Flex minH="100vh" align="center" justify="center" bg="bg">
      <Box 
        w="full" 
        maxW="md" 
        p={8} 
        borderRadius="lg" 
        bg="bg.surface" 
        border="1px solid" 
        borderColor="border"
        boxShadow="xl"
      >
        <VStack spacing={6}>
          <Box textAlign="center">
            <Text fontSize="2xl" fontWeight="bold" color="text">
              Bienvenido a GENIUS INDUSTRIES
            </Text>
            <Text color="text.muted" mt={2}>
              Inicia sesión para acceder a tu dashboard
            </Text>
          </Box>
          <SignIn 
            appearance={{
              elements: {
                rootBox: "w-full",
                card: "bg-transparent shadow-none border-none",
              }
            }}
            signUpUrl="/sign-up"
            redirectUrl="/admin"
          />
        </VStack>
      </Box>
    </Flex>
  )
}

export function SignUpPage() {
  return (
    <Flex minH="100vh" align="center" justify="center" bg="bg">
      <Box 
        w="full" 
        maxW="md" 
        p={8} 
        borderRadius="lg" 
        bg="bg.surface" 
        border="1px solid" 
        borderColor="border"
        boxShadow="xl"
      >
        <VStack spacing={6}>
          <Box textAlign="center">
            <Text fontSize="2xl" fontWeight="bold" color="text">
              Registro de Cliente - GENIUS INDUSTRIES
            </Text>
            <Text color="text.muted" mt={2}>
              Crea tu cuenta de cliente para acceder a nuestros servicios
            </Text>
            
            {/* Aviso importante sobre restricciones de registro */}
            <Box 
              mt={4} 
              p={4} 
              bg="blue.50" 
              borderRadius="lg" 
              border="1px solid" 
              borderColor="blue.200"
            >
              <HStack spacing={2} justify="center" mb={2}>
                <Text fontSize="sm" color="blue.700" fontWeight="bold">
                  ℹ️ INFORMACIÓN IMPORTANTE
                </Text>
              </HStack>
              <Text fontSize="sm" color="blue.700" textAlign="left">
                <strong>Registro disponible únicamente para clientes.</strong>
              </Text>
              <Text fontSize="xs" color="blue.600" mt={2} textAlign="left">
                Los usuarios corporativos (CEO, Manager, Supervisor, HR, Agentes, Soporte) 
                son creados y gestionados exclusivamente por el administrador principal del sistema.
              </Text>
              <Text fontSize="xs" color="blue.600" mt={1} textAlign="left">
                Si eres un empleado de GENIUS INDUSTRIES, contacta al CEO para obtener acceso.
              </Text>
            </Box>
          </Box>
          
          <SignUp 
            appearance={{
              elements: {
                rootBox: "w-full",
                card: "bg-transparent shadow-none border-none",
              }
            }}
            signInUrl="/sign-in"
            redirectUrl="/client-dashboard"
          />
          
          <Box textAlign="center" pt={4} borderTop="1px solid" borderColor="border">
            <Text fontSize="xs" color="text.muted">
              ¿Ya tienes una cuenta? 
              <Text as="span" color="blue.500" fontWeight="medium" ml={1}>
                <a href="/sign-in">Inicia sesión aquí</a>
              </Text>
            </Text>
          </Box>
        </VStack>
      </Box>
    </Flex>
  )
}

export function UserProfile() {
  const { user } = useUser()
  const { signOut } = useAuth()

  return (
    <HStack spacing={4} align="center">
      <Text color="text.muted" fontSize="sm">
        Hola, {user?.firstName || user?.emailAddresses[0]?.emailAddress}
      </Text>
      <UserButton 
        appearance={{
          elements: {
            rootBox: "rounded-full",
            avatarBox: "border-2 border-border",
          }
        }}
        showName={false}
      />
    </HStack>
  )
}

export function RoleBasedAccess({ 
  allowedRoles, 
  children, 
  fallback 
}: { 
  allowedRoles: string[]
  children: React.ReactNode
  fallback?: React.ReactNode
}) {
  const { user } = useUser()
  const userRole = user?.publicMetadata?.role as string

  if (!allowedRoles.includes(userRole)) {
    return fallback ? <>{fallback}</> : null
  }

  return <>{children}</>
} 
