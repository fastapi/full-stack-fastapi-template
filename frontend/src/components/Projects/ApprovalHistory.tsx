import { Box, Card, Flex, Heading, Stack, Text } from "@chakra-ui/react"
import { FiCheckCircle, FiClock, FiAlertCircle, FiUpload } from "react-icons/fi"

interface ApprovalHistoryProps {
  gallery: any
}

export function ApprovalHistory({ gallery }: ApprovalHistoryProps) {
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
    <Card.Root>
      <Card.Header>
        <Heading size="md">Approval History</Heading>
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
                  bg={`${item.color}.100`}
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  color={`${item.color}.600`}
                >
                  {item.icon}
                </Box>
                {index < timeline.length - 1 && (
                  <Box w="2px" h="40px" bg="gray.200" mt={2} />
                )}
              </Flex>

              {/* Content */}
              <Box flex={1} pt={2}>
                <Text fontWeight="semibold">{item.label}</Text>
                <Text fontSize="xs" color="fg.muted">
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