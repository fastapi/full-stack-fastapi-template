import {
  Box,
  Button,
  Container,
  Heading,
  Input,
  SimpleGrid,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { useQuery, useQueryClient } from "@tanstack/react-query"

import { PaymentsService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { Field } from "../ui/field"
import { Table } from "@chakra-ui/react"

const Checkout = () => {
  const navigate = useNavigate()
  const { showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [isProcessing, setIsProcessing] = useState(false)
  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<{ amount: number; currency: string }>({
    mode: "onBlur",
    defaultValues: {
      amount: 1, // Default 1 INR
      currency: "INR",
    },
  })

  // Fetch payment analytics
  const { data: ordersData, isLoading } = useQuery({
    queryKey: ["orders"],
    queryFn: () => PaymentsService.readOrders({}),
  })

  const onSubmit: SubmitHandler<{ amount: number; currency: string }> = async (
    data
  ) => {
    if (isProcessing) return

    setIsProcessing(true)

    try {
      // Convert rupees to paise (multiply by 100)
      const amountInPaise = Math.round(data.amount * 100)
      
      // Create order using generated client
      const orderData = await PaymentsService.createOrder({
        requestBody: {
          amount: amountInPaise,
          currency: data.currency,
        },
      })

      // Open Razorpay Checkout
      if (!(window as any).Razorpay) {
        showErrorToast("Razorpay checkout is not loaded. Please refresh the page.")
        setIsProcessing(false)
        return
      }

      const options = {
        key: orderData.key,
        amount: orderData.amount,
        currency: orderData.currency,
        name: "FastAPI Payment",
        description: "Payment for order",
        order_id: orderData.id,
        handler: async (response: {
          razorpay_payment_id: string
          razorpay_order_id: string
          razorpay_signature: string
        }) => {
          try {
            // Verify payment on backend using generated client
            await PaymentsService.verifyPayment({
              requestBody: {
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              },
            })

            // Invalidate orders query to refresh the list
            queryClient.invalidateQueries({ queryKey: ["orders"] })
            
            // Redirect to success page
            navigate({
              to: "/payment-success",
              search: {
                order_id: response.razorpay_order_id,
                payment_id: response.razorpay_payment_id,
              },
            })
          } catch (error) {
            handleError(error as ApiError)
            navigate({
              to: "/payment-failure",
              search: {
                error: "Payment verification failed",
              },
            })
          }
        },
        prefill: {
          name: "",
          email: "",
          contact: "",
        },
        theme: {
          color: "#2563eb", // Blue theme color
        },
        modal: {
          ondismiss: () => {
            setIsProcessing(false)
          },
        },
      }

      const rzp = new (window as any).Razorpay(options)
      rzp.open()
    } catch (error) {
      handleError(error as ApiError)
      setIsProcessing(false)
    }
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
        {/* Payment Form Section */}
        <Box p={6} borderWidth="1px" borderRadius="md" bg="bg.surface">
          <Heading size="lg" mb={4}>Make a Payment</Heading>
          <Text mb={6} color="fg.muted">Enter the amount you want to pay</Text>
          <form onSubmit={handleSubmit(onSubmit)}>
            <VStack gap={4} align="stretch" maxW="md">
              <Field
                required
                invalid={!!errors.amount}
                errorText={errors.amount?.message}
                label="Amount (in ₹)"
              >
                <Input
                  {...register("amount", {
                    required: "Amount is required",
                    min: {
                      value: 1,
                      message: "Amount must be at least ₹1",
                    },
                    valueAsNumber: true,
                  })}
                  placeholder="Enter amount in rupees"
                  type="number"
                  step="0.01"
                />
              </Field>

              <Field
                required
                invalid={!!errors.currency}
                errorText={errors.currency?.message}
                label="Currency"
              >
                <Input
                  {...register("currency", {
                    required: "Currency is required",
                  })}
                  placeholder="Currency"
                  type="text"
                  readOnly
                />
              </Field>

              <Button
                variant="solid"
                colorPalette="blue"
                type="submit"
                disabled={!isValid || isProcessing}
                loading={isProcessing}
                size="lg"
                width="100%"
              >
                Pay Now
              </Button>
            </VStack>
          </form>
        </Box>

        {/* Payment Analytics Dashboard Section */}
        <Box p={6} borderWidth="1px" borderRadius="md" bg="bg.surface">
          <Heading size="lg" mb={6}>Payment Dashboard</Heading>
          
          {/* Statistics Cards */}
          <SimpleGrid columns={{ base: 1, md: 3 }} gap={4} mb={6}>
            <Box p={4} borderWidth="1px" borderRadius="md" bg="blue.50" borderColor="blue.200">
              <Text fontSize="sm" fontWeight="bold" mb={1} color="blue.700">Total Spent</Text>
              <Text fontSize="2xl" fontWeight="bold" color="blue.600">
                ₹{(totalAmount / 100).toFixed(2)}
              </Text>
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

          {/* Recent Orders Table */}
          <Box>
            <Heading size="md" mb={4}>Recent Orders</Heading>
            {isLoading ? (
              <Text>Loading orders...</Text>
            ) : (
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
                        <Text 
                          textTransform="capitalize"
                          color={order.status === "paid" ? "blue.600" : order.status === "failed" ? "red.600" : "gray.600"}
                          fontWeight={order.status === "paid" ? "bold" : "normal"}
                        >
                          {order.status}
                        </Text>
                      </Table.Cell>
                      <Table.Cell>
                        {new Date(order.created_at).toLocaleDateString()}
                      </Table.Cell>
                    </Table.Row>
                  ))}
                  {orders.length === 0 && (
                    <Table.Row>
                      <Table.Cell colSpan={4} textAlign="center">
                        <Text>No orders found. Make your first payment above!</Text>
                      </Table.Cell>
                    </Table.Row>
                  )}
                </Table.Body>
              </Table.Root>
            )}
          </Box>
        </Box>
      </VStack>
    </Container>
  )
}

export default Checkout

