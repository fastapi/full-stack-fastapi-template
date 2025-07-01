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
            redirectUrl="/dashboard"
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
              Únete a GENIUS INDUSTRIES
            </Text>
            <Text color="text.muted" mt={2}>
              Crea tu cuenta para comenzar
            </Text>
          </Box>
          <SignUp 
            appearance={{
              elements: {
                rootBox: "w-full",
                card: "bg-transparent shadow-none border-none",
              }
            }}
            signInUrl="/sign-in"
            redirectUrl="/dashboard"
          />
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