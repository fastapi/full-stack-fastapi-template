import { createFileRoute, redirect } from '@tanstack/react-router'
import { SignIn } from '@clerk/clerk-react'
import { Box, Heading, Text } from '@chakra-ui/react'
import { useAuth } from '@/hooks/useAuth'

export const Route = createFileRoute('/login')({
  component: LoginPage,
  beforeLoad: async () => {
    const { isSignedIn } = useAuth()
    if (isSignedIn) {
      throw redirect({ to: '/admin' })
    }
  },
})

function LoginPage() {
  return (
    <Box minH="100vh" display="flex" alignItems="center" justifyContent="center" bg="bg" p={4}>
      <Box maxW="md" mx="auto" p={8} bg="bg.surface" borderRadius="md" shadow="md" border="1px" borderColor="border">
        <Heading size="lg" color="text" textAlign="center" mb={6}>
          Iniciar Sesión
        </Heading>
        <Text color="text.muted" textAlign="center" mb={6}>
          Accede a tu cuenta de Genius Industries
        </Text>
        <SignIn 
          routing="path" 
          path="/login"
          redirectUrl="/admin"
          appearance={{
            baseTheme: 'dark',
            elements: {
              formButtonPrimary: 'bg-blue-600 hover:bg-blue-700',
              card: 'bg-transparent shadow-none',
              headerTitle: 'text-white',
              headerSubtitle: 'text-gray-300',
              socialButtonsBlockButton: 'border-gray-600 text-white hover:bg-gray-700',
              formFieldInput: 'bg-gray-800 border-gray-600 text-white',
              formFieldLabel: 'text-gray-300',
              identityPreviewText: 'text-white',
              identityPreviewEditButton: 'text-blue-400'
            }
          }}
        />
      </Box>
    </Box>
  )
}
