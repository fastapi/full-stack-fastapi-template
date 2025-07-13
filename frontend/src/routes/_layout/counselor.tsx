import {
  Badge,
  Box,
  Button,
  Container,
  Flex,
  Grid,
  HStack,
  Heading,
  Text,
  VStack,
  Spinner,
  Textarea,
} from "@chakra-ui/react"
import { useMutation, useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import {
  FiClock,
  FiCheckCircle,
  FiX,
  FiEdit,
} from "react-icons/fi"

import { CounselorService } from "@/client"
import { RoleGuard } from "@/components/Common/RoleGuard"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "@/components/ui/dialog"
import { Field } from "@/components/ui/field"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/_layout/counselor")({
  component: CounselorDashboard,
})

function CounselorDashboard() {
  return (
    <RoleGuard permission="access_counselor_queue">
      <CounselorDashboardContent />
    </RoleGuard>
  )
}

function CounselorDashboardContent() {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [selectedResponse, setSelectedResponse] = useState<any>(null)
  const [isModifyDialogOpen, setIsModifyDialogOpen] = useState(false)
  const [modifiedResponse, setModifiedResponse] = useState("")
  const [counselorNotes, setCounselorNotes] = useState("")
  const [isRejectDialogOpen, setIsRejectDialogOpen] = useState(false)
  const [replacementResponse, setReplacementResponse] = useState("")
  const [rejectionReason, setRejectionReason] = useState("")

  // Fetch counselor queue
  const { data: queueData, isLoading, error, refetch } = useQuery({
    queryKey: ["counselor-queue"],
    queryFn: () => CounselorService.getCounselorQueue({ limit: 50 }),
    refetchInterval: 30000, // Refetch every 30 seconds for better responsiveness
    refetchIntervalInBackground: true, // Keep refetching in background
    retry: (failureCount, error: any) => {
      // Don't retry on 403 errors (permission issues)
      if (error?.status === 403) return false
      // Retry up to 3 times for other errors
      return failureCount < 3
    },
  })

  // Fetch performance metrics
  const { data: performanceData } = useQuery({
    queryKey: ["counselor-performance"],
    queryFn: () => CounselorService.getCounselorPerformance({ days: 7 }),
  })

  // Approve response mutation
  const approveMutation = useMutation({
    mutationFn: (data: { responseId: string; notes?: string }) =>
      CounselorService.approveResponse({
        pendingResponseId: data.responseId,
        requestBody: { notes: data.notes },
      }),
    onSuccess: () => {
      showSuccessToast("Response approved successfully")
      refetch()
    },
    onError: () => {
      showErrorToast("Failed to approve response")
    },
  })

  // Modify response mutation
  const modifyMutation = useMutation({
    mutationFn: (data: { responseId: string; modifiedResponse: string; notes?: string }) =>
      CounselorService.modifyResponse({
        pendingResponseId: data.responseId,
        requestBody: {
          modified_response: data.modifiedResponse,
          notes: data.notes,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Response modified and sent successfully")
      setIsModifyDialogOpen(false)
      setSelectedResponse(null)
      setModifiedResponse("")
      setCounselorNotes("")
      refetch()
    },
    onError: () => {
      showErrorToast("Failed to modify response")
    },
  })

  // Reject response mutation
  const rejectMutation = useMutation({
    mutationFn: (data: { responseId: string; replacementResponse: string; reason: string }) =>
      CounselorService.rejectResponse({
        pendingResponseId: data.responseId,
        requestBody: {
          replacement_response: data.replacementResponse,
          reason: data.reason,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Response rejected and replacement sent successfully")
      setIsRejectDialogOpen(false)
      setSelectedResponse(null)
      setReplacementResponse("")
      setRejectionReason("")
      refetch()
    },
    onError: () => {
      showErrorToast("Failed to reject response")
    },
  })

  const handleApprove = (responseId: string) => {
    approveMutation.mutate({ responseId })
  }

  const handleModify = (response: any) => {
    setSelectedResponse(response)
    setModifiedResponse(response.ai_generated_response || "")
    setIsModifyDialogOpen(true)
  }

  const handleReject = (response: any) => {
    setSelectedResponse(response)
    setReplacementResponse("")
    setRejectionReason("")
    setIsRejectDialogOpen(true)
  }

  const handleSubmitModification = () => {
    if (selectedResponse && modifiedResponse.trim()) {
      modifyMutation.mutate({
        responseId: selectedResponse.id,
        modifiedResponse: modifiedResponse.trim(),
        notes: counselorNotes.trim() || undefined,
      })
    }
  }

  const handleSubmitRejection = () => {
    if (selectedResponse && replacementResponse.trim() && rejectionReason.trim()) {
      rejectMutation.mutate({
        responseId: selectedResponse.id,
        replacementResponse: replacementResponse.trim(),
        reason: rejectionReason.trim(),
      })
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case "urgent":
        return "red"
      case "high":
        return "orange"
      case "normal":
        return "blue"
      case "low":
        return "gray"
      default:
        return "gray"
    }
  }

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case "critical":
        return "red"
      case "high":
        return "orange"
      case "medium":
        return "yellow"
      case "low":
        return "green"
      default:
        return "gray"
    }
  }

  if (isLoading) {
    return (
      <Container maxW="7xl" py={8}>
        <Flex justify="center" align="center" h="200px">
          <Spinner size="lg" />
        </Flex>
      </Container>
    )
  }

  if (error) {
    return (
      <Container maxW="7xl" py={8}>
        <Box textAlign="center" py={10}>
          <Heading size="lg" mb={4}>
            Unable to Load Counselor Dashboard
          </Heading>
          <Text color="gray.600" mb={4}>
            {error?.message || "There was an error loading the counselor queue. Please try again or contact support."}
          </Text>
          <Button onClick={() => refetch()} colorScheme="blue">
            Try Again
          </Button>
        </Box>
      </Container>
    )
  }

  return (
    <Container maxW="7xl" py={8}>
      <VStack gap={8} align="stretch">
        {/* Header */}
        <Flex justify="space-between" align="center">
          <Box>
            <Heading size="lg" mb={2}>
              Counselor Dashboard
            </Heading>
            <Text color="gray.600">
              Review AI responses and manage high-risk conversations
            </Text>
          </Box>
          <Button onClick={() => refetch()} colorScheme="teal">
            Refresh Queue
          </Button>
        </Flex>

        {/* Stats Cards */}
        <Grid templateColumns={{ base: "1fr", md: "repeat(4, 1fr)" }} gap={6}>
          <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
            <VStack align="start">
              <Text fontSize="sm" color="gray.500" fontWeight="medium">
                Pending Reviews
              </Text>
              <Heading size="lg" color="blue.600">
                {queueData?.total_count || 0}
              </Heading>
            </VStack>
          </Box>
          
          <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
            <VStack align="start">
              <Text fontSize="sm" color="gray.500" fontWeight="medium">
                Urgent Cases
              </Text>
              <Heading size="lg" color="red.600">
                {queueData?.urgent_count || 0}
              </Heading>
            </VStack>
          </Box>
          
          <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
            <VStack align="start">
              <Text fontSize="sm" color="gray.500" fontWeight="medium">
                High Priority
              </Text>
              <Heading size="lg" color="orange.600">
                {queueData?.high_priority_count || 0}
              </Heading>
            </VStack>
          </Box>

          <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
            <VStack align="start">
              <Text fontSize="sm" color="gray.500" fontWeight="medium">
                Cases Reviewed (7d)
              </Text>
              <Heading size="lg" color="green.600">
                {performanceData?.total_cases_reviewed || 0}
              </Heading>
            </VStack>
          </Box>
        </Grid>

        {/* Review Queue */}
        <Box p={6} bg="white" borderRadius="lg" shadow="sm" border="1px" borderColor="gray.200">
          <Heading size="md" mb={6}>
            Pending Response Reviews
          </Heading>
          
          {queueData?.queue_items && queueData.queue_items.length > 0 ? (
            <VStack gap={4} align="stretch">
              {queueData.queue_items.map((item: any) => (
                <Box
                  key={item.id}
                  p={4}
                  border="1px"
                  borderColor="gray.200"
                  borderRadius="md"
                  bg="gray.50"
                >
                  <VStack align="stretch" gap={3}>
                    <Flex justify="space-between" align="center">
                      <HStack>
                        <Badge colorScheme={getPriorityColor(item.priority)}>
                          {item.priority || "Normal"} Priority
                        </Badge>
                        <Badge colorScheme={getRiskLevelColor(item.risk_level)}>
                          {item.risk_level || "Unknown"} Risk
                        </Badge>
                        <Text fontSize="sm" color="gray.500">
                          <FiClock style={{ display: "inline", marginRight: "4px" }} />
                          {new Date(item.created_at).toLocaleString()}
                        </Text>
                      </HStack>
                    </Flex>

                    <Box>
                      <Text fontWeight="medium" mb={2}>
                        User Message:
                      </Text>
                      <Text
                        p={3}
                        bg="blue.50"
                        borderRadius="md"
                        borderLeft="4px"
                        borderColor="blue.500"
                      >
                        {item.original_user_message}
                      </Text>
                    </Box>

                    <Box>
                      <Text fontWeight="medium" mb={2}>
                        AI Generated Response:
                      </Text>
                      <Text
                        p={3}
                        bg="gray.100"
                        borderRadius="md"
                        borderLeft="4px"
                        borderColor="gray.500"
                      >
                        {item.ai_generated_response}
                      </Text>
                    </Box>

                    {item.risk_categories && (
                      <Box>
                        <Text fontWeight="medium" mb={2}>
                          Risk Categories:
                        </Text>
                        <Text fontSize="sm" color="red.600">
                          {item.risk_categories}
                        </Text>
                      </Box>
                    )}

                    <HStack gap={2}>
                      <Button
                        size="sm"
                        colorScheme="green"
                        onClick={() => handleApprove(item.id)}
                        loading={approveMutation.isPending}
                      >
                        <FiCheckCircle style={{ marginRight: "4px" }} />
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        colorScheme="blue"
                        onClick={() => handleModify(item)}
                      >
                        <FiEdit style={{ marginRight: "4px" }} />
                        Modify
                      </Button>
                      <Button
                        size="sm"
                        colorScheme="red"
                        variant="outline"
                        onClick={() => handleReject(item)}
                      >
                        <FiX style={{ marginRight: "4px" }} />
                        Reject
                      </Button>
                    </HStack>
                  </VStack>
                </Box>
              ))}
            </VStack>
          ) : (
            <Box textAlign="center" py={8}>
              <Text color="gray.500">No pending reviews at this time</Text>
            </Box>
          )}
        </Box>

        {/* Modify Response Dialog */}
        <DialogRoot
          open={isModifyDialogOpen}
          onOpenChange={({ open }) => setIsModifyDialogOpen(open)}
          size="xl"
        >
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Modify AI Response</DialogTitle>
            </DialogHeader>
            <DialogBody>
              <VStack gap={4} align="stretch">
                {selectedResponse && (
                  <Box>
                    <Text fontWeight="medium" mb={2}>
                      Original User Message:
                    </Text>
                    <Text
                      p={3}
                      bg="blue.50"
                      borderRadius="md"
                      fontSize="sm"
                    >
                      {selectedResponse.original_user_message}
                    </Text>
                  </Box>
                )}

                <Field label="Modified Response" required>
                  <Textarea
                    value={modifiedResponse}
                    onChange={(e) => setModifiedResponse(e.target.value)}
                    placeholder="Edit the AI response..."
                    rows={6}
                  />
                </Field>

                <Field label="Counselor Notes (Optional)">
                  <Textarea
                    value={counselorNotes}
                    onChange={(e) => setCounselorNotes(e.target.value)}
                    placeholder="Add notes about your modifications..."
                    rows={3}
                  />
                </Field>
              </VStack>
            </DialogBody>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsModifyDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button
                colorScheme="blue"
                onClick={handleSubmitModification}
                loading={modifyMutation.isPending}
                disabled={!modifiedResponse.trim()}
              >
                Send Modified Response
              </Button>
            </DialogFooter>
            <DialogCloseTrigger />
          </DialogContent>
        </DialogRoot>

        {/* Reject Response Dialog */}
        <DialogRoot
          open={isRejectDialogOpen}
          onOpenChange={({ open }) => setIsRejectDialogOpen(open)}
          size="xl"
        >
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Reject AI Response</DialogTitle>
            </DialogHeader>
            <DialogBody>
              <VStack gap={4} align="stretch">
                {selectedResponse && (
                  <Box>
                    <Text fontWeight="medium" mb={2}>
                      Original User Message:
                    </Text>
                    <Text
                      p={3}
                      bg="blue.50"
                      borderRadius="md"
                      fontSize="sm"
                    >
                      {selectedResponse.original_user_message}
                    </Text>
                  </Box>
                )}

                <Field label="Replacement Response" required>
                  <Textarea
                    value={replacementResponse}
                    onChange={(e) => setReplacementResponse(e.target.value)}
                    placeholder="Provide a replacement response..."
                    rows={6}
                  />
                </Field>

                <Field label="Rejection Reason" required>
                  <Textarea
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    placeholder="Explain why this response is being rejected..."
                    rows={3}
                  />
                </Field>
              </VStack>
            </DialogBody>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsRejectDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button
                colorScheme="red"
                onClick={handleSubmitRejection}
                loading={rejectMutation.isPending}
                disabled={!replacementResponse.trim() || !rejectionReason.trim()}
              >
                Send Rejection
              </Button>
            </DialogFooter>
            <DialogCloseTrigger />
          </DialogContent>
        </DialogRoot>
      </VStack>
    </Container>
  )
} 