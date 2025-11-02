import {
  Box,
  Container,
  Heading,
  SimpleGrid,
  Table,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"

import { PaymentsService } from "@/client"

const PaymentAnalytics = () => {
  const { data: ordersData, isLoading } = useQuery({
    queryKey: ["orders"],
    queryFn: () => PaymentsService.readOrders({}),
  })

  if (isLoading) {
    return <Text>Loading analytics...</Text>
  }

  const orders = ordersData?.data || []
  const totalAmount = orders.reduce(
    (sum: number, order: { amount: string | number }) => sum + parseInt(String(order.amount)),
    0
  )
  const successfulPayments = orders.filter(
    (order: { status: string }) => order.status === "paid"
  ).length
  const failedPayments = orders.filter(
    (order: { status: string }) => order.status === "failed"
  ).length

  return (
    <Container maxW="full" py={8}>
      <VStack gap={6} align="stretch">
        <Heading size="lg">Payment Analytics</Heading>

        <SimpleGrid columns={{ base: 1, md: 3 }} gap={4}>
          <Box p={4} borderWidth="1px" borderRadius="md" bg="blue.50" borderColor="blue.200">
            <Text fontSize="sm" fontWeight="bold" mb={1} color="blue.700">Total Spent</Text>
            <Text fontSize="2xl" fontWeight="bold" color="blue.600">₹{(totalAmount / 100).toFixed(2)}</Text>
          </Box>
          <Box p={4} borderWidth="1px" borderRadius="md" bg="blue.50" borderColor="blue.200">
            <Text fontSize="sm" fontWeight="bold" mb={1} color="blue.700">Successful Payments</Text>
            <Text fontSize="2xl" fontWeight="bold" color="blue.600">{successfulPayments}</Text>
          </Box>
          <Box p={4} borderWidth="1px" borderRadius="md" bg="blue.50" borderColor="blue.200">
            <Text fontSize="sm" fontWeight="bold" mb={1} color="blue.700">Failed Payments</Text>
            <Text fontSize="2xl" fontWeight="bold" color="blue.600">{failedPayments}</Text>
          </Box>
        </SimpleGrid>

        <Box p={4} borderWidth="1px" borderRadius="md">
          <Heading size="md" mb={4}>
            Recent Orders
          </Heading>
          <Table.Root size={{ base: "sm", md: "md" }}>
            <Table.Header>
              <Table.Row>
                <Table.ColumnHeader>Order ID</Table.ColumnHeader>
                <Table.ColumnHeader>Amount</Table.ColumnHeader>
                <Table.ColumnHeader>Status</Table.ColumnHeader>
                <Table.ColumnHeader>Date</Table.ColumnHeader>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {orders.slice(0, 10).map((order: any) => (
                <Table.Row key={order.id}>
                  <Table.Cell>
                    <Text fontSize="xs" maxW="200px" style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {order.razorpay_order_id}
                    </Text>
                  </Table.Cell>
                  <Table.Cell>₹{(parseInt(String(order.amount)) / 100).toFixed(2)}</Table.Cell>
                  <Table.Cell>
                    <Text textTransform="capitalize">{order.status}</Text>
                  </Table.Cell>
                  <Table.Cell>
                    {new Date(order.created_at).toLocaleDateString()}
                  </Table.Cell>
                </Table.Row>
              ))}
              {orders.length === 0 && (
                <Table.Row>
                  <Table.Cell colSpan={4} textAlign="center">
                    <Text>No orders found</Text>
                  </Table.Cell>
                </Table.Row>
              )}
            </Table.Body>
          </Table.Root>
        </Box>
      </VStack>
    </Container>
  )
}

export default PaymentAnalytics

