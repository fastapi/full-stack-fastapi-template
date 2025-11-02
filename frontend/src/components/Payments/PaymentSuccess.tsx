import {
  Box,
  Button,
  Container,
  Heading,
  HStack,
  SimpleGrid,
  Text,
  VStack,
} from "@chakra-ui/react"
import { Link, useSearch } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import { FaCheckCircle } from "react-icons/fa"

import { PaymentsService } from "@/client"

interface PaymentSuccessSearch {
  order_id?: string
  payment_id?: string
}

const PaymentSuccess = () => {
  const search = useSearch({ from: "/payment-success" }) as PaymentSuccessSearch
  const { order_id, payment_id } = search || {}

  // Fetch order details for analytics
  const { data: orderData, isLoading } = useQuery({
    queryKey: ["order", order_id],
    queryFn: async () => {
      if (!order_id) return null
      const data = await PaymentsService.readOrders({})
      // Find the specific order
      return data.data?.find(
        (o: { razorpay_order_id: string }) => o.razorpay_order_id === order_id
      )
    },
    enabled: !!order_id,
  })

  return (
    <Container maxW="2xl" py={8}>
      <VStack gap={6} align="stretch">
        <Box p={6} borderWidth="1px" borderRadius="md">
          <VStack gap={4} align="center">
            <FaCheckCircle size={64} color="#2563eb" />
            <Heading size="lg" color="blue.600">
              Payment Successful!
            </Heading>
            <Text textAlign="center">
              Your payment has been processed successfully.
            </Text>
          </VStack>
        </Box>

        <Box p={6} borderWidth="1px" borderRadius="md">
          <Heading size="md" mb={4}>
            Payment Details
          </Heading>
          <SimpleGrid columns={{ base: 1, md: 2 }} gap={4}>
            {order_id && (
              <Box>
                <Text fontSize="sm" fontWeight="bold" mb={1}>Order ID</Text>
                <Text fontSize="sm" wordBreak="break-all">
                  {order_id}
                </Text>
              </Box>
            )}
            {payment_id && (
              <Box>
                <Text fontSize="sm" fontWeight="bold" mb={1}>Payment ID</Text>
                <Text fontSize="sm" wordBreak="break-all">
                  {payment_id}
                </Text>
              </Box>
            )}
            {orderData && (
              <>
                <Box>
                  <Text fontSize="sm" fontWeight="bold" mb={1}>Amount</Text>
                  <Text>
                    ₹{(parseInt(String(orderData.amount)) / 100).toFixed(2)}
                  </Text>
                </Box>
                <Box>
                  <Text fontSize="sm" fontWeight="bold" mb={1}>Status</Text>
                  <Text textTransform="capitalize">{orderData.status}</Text>
                </Box>
              </>
            )}
          </SimpleGrid>
        </Box>

        <Box p={6} borderWidth="1px" borderRadius="md">
          <Heading size="md" mb={4}>
            Database Updates Analytics
          </Heading>
          <VStack gap={3} align="stretch">
            <Text>
              ✅ <strong>Order record created</strong> in database with status:
              {orderData?.status || "paid"}
            </Text>
            <Text>
              ✅ <strong>Payment record added</strong> to database with payment ID:
              {payment_id || "N/A"}
            </Text>
            <Text>
              ✅ <strong>User payment history updated</strong> - This transaction has
              been added to your order history
            </Text>
            {isLoading && <Text>Loading order details...</Text>}
            {orderData && (
              <Text>
                ✅ <strong>Order timestamp:</strong>{" "}
                {new Date(orderData.created_at).toLocaleString()}
              </Text>
            )}
          </VStack>
        </Box>

        <HStack gap={4} justify="center">
          <Link to="/checkout">
            <Button variant="outline">Make Another Payment</Button>
          </Link>
          <Link to="/">
            <Button variant="solid">Back to Dashboard</Button>
          </Link>
        </HStack>
      </VStack>
    </Container>
  )
}

export default PaymentSuccess

