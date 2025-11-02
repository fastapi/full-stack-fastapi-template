import {
  Box,
  Button,
  Container,
  Heading,
  HStack,
  Text,
  VStack,
} from "@chakra-ui/react"
import { Link, useSearch } from "@tanstack/react-router"
import { FaExclamationTriangle } from "react-icons/fa"

interface PaymentFailureSearch {
  error?: string
}

const PaymentFailure = () => {
  const search = useSearch({ from: "/payment-failure" }) as PaymentFailureSearch
  const { error } = search || {}

  return (
    <Container maxW="md" py={8}>
      <Box p={6} borderWidth="1px" borderRadius="md">
        <VStack gap={6} align="center">
          <FaExclamationTriangle size={64} color="#e53e3e" />
          <Heading size="lg" color="red.600">
            Payment Failed
          </Heading>
          <Text textAlign="center">
            {error || "Your payment could not be processed. Please try again."}
          </Text>
          <Text fontSize="sm" color="gray.500" textAlign="center">
            If you were charged, the amount will be refunded to your account within
            5-7 business days.
          </Text>

          <HStack gap={4} mt={4}>
            <Link to="/checkout">
              <Button variant="solid" colorPalette="blue">
                Retry Payment
              </Button>
            </Link>
            <Link to="/">
              <Button variant="outline">Back to Dashboard</Button>
            </Link>
          </HStack>
        </VStack>
      </Box>
    </Container>
  )
}

export default PaymentFailure

