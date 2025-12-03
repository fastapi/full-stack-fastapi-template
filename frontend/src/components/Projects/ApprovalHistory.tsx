import { Box, Card, Flex, Heading, Stack, Text } from "@chakra-ui/react"
import { FiCheckCircle, FiClock, FiAlertCircle, FiUpload } from "react-icons/fi"

interface ApprovalHistoryProps {
  gallery: any
}

export function ApprovalHistory({ gallery }: ApprovalHistoryProps) {
  // Color mapping for Navy & Gold theme
  const colorMap: Record<string, { bg: string; icon: string }> = {
    gray: { bg: "#F1F5F9", icon: "#64748B" },
    blue: { bg: "#DBEAFE", icon: "#1E40AF" },
    green: { bg: "#D1FAE5", icon: "#059669" },
    orange: { bg: "#FED7AA", icon: "#EA580C" },
  }

  // Generate timeline based on gallery status
  const getTimeline = () => {
    const timeline = [
      {
        status: "draft",
        label: "Created",
        icon: <FiClock />,
        color: "gray",
        completed: true,
        timestamp: gallery.created_at,
      },
    ]

    if (
      gallery.status === "pending_review" ||
      gallery.status === "approved" ||
      gallery.status === "changes_requested"
    ) {
      timeline.push({
        status: "pending_review",
        label: "Submitted for Review",
        icon: <FiUpload />,
        color: "blue",
        completed: true,
        timestamp: gallery.created_at, // Using created_at as proxy
      })
    }

    if (gallery.status === "approved") {
      timeline.push({
        status: "approved",
        label: "Approved",
        icon: <FiCheckCircle />,
        color: "green",
        completed: true,
        timestamp: gallery.created_at,
      })
    }

    if (gallery.status === "changes_requested") {
      timeline.push({
        status: "changes_requested",
        label: "Changes Requested",
        icon: <FiAlertCircle />,
        color: "orange",
        completed: true,
        timestamp: gallery.created_at,
      })
    }

    return timeline
  }

  const timeline = getTimeline()

  const formatDate = (dateString: string) => {
    const date = new Date(dateString + "Z")
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <Card.Root bg="white" borderColor="#E2E8F0">
      <Card.Header>
        <Heading size="md" color="#1E3A8A">Approval History</Heading>
      </Card.Header>
      <Card.Body>
        <Stack gap={4}>
          {timeline.map((item, index) => (
            <Flex key={item.status} gap={4} alignItems="start">
              {/* Timeline line and dot */}
              <Flex direction="column" alignItems="center">
                <Box
                  w="40px"
                  h="40px"
                  borderRadius="full"
                  bg={colorMap[item.color].bg}
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  color={colorMap[item.color].icon}
                >
                  {item.icon}
                </Box>
                {index < timeline.length - 1 && (
                  <Box w="2px" h="40px" bg="#E2E8F0" mt={2} />
                )}
              </Flex>

              {/* Content */}
              <Box flex={1} pt={2}>
                <Text fontWeight="semibold" color="#1E293B">{item.label}</Text>
                <Text fontSize="xs" color="#64748B">
                  {formatDate(item.timestamp)}
                </Text>
              </Box>
            </Flex>
          ))}
        </Stack>
      </Card.Body>
    </Card.Root>
  )
}