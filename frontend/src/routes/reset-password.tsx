import { createFileRoute } from '@tanstack/react-router'
import { Box, Heading, Text } from '@chakra-ui/react'

export const Route = createFileRoute('/reset-password')({
  component: ResetPasswordPage,
})

function ResetPasswordPage() {
  return (
    <Box minH="100vh" display="flex" alignItems="center" justifyContent="center" bg="bg" p={4}>
      <Box maxW="md" mx="auto" p={8} bg="bg.surface" borderRadius="md" shadow="md" border="1px" borderColor="border">
        <Heading size="lg" color="text" textAlign="center" mb={6}>
          Restablecer Contraseña
        </Heading>
        <Text color="text.muted" textAlign="center" mb={6}>
          Ingresa tu nueva contraseña
        </Text>
        {/* Aquí iría el formulario de restablecimiento */}
        <Text color="text.subtle" textAlign="center" fontSize="sm">
          Funcionalidad en desarrollo
        </Text>
      </Box>
    </Box>
  )
}
