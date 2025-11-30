import { Badge, Box, Flex, Text } from "@chakra-ui/react"
import type { ProjectPublic } from "@/client"

interface ProjectTimelineProps {
  project: ProjectPublic
}

export function ProjectTimeline({ project }: ProjectTimelineProps) {
  const startDate = project.start_date ? new Date(project.start_date) : null
  const deadline = project.deadline ? new Date(project.deadline) : null
  const today = new Date()

  const workProgressRaw = project.progress ?? 0
  const workProgress = Math.max(0, Math.min(100, workProgressRaw))

  // Time-based progress: how far between start and deadline "today" is
  const getTimeProgress = () => {
    if (!startDate || !deadline) return 0
    const total = deadline.getTime() - startDate.getTime()
    if (total <= 0) return 0
    const elapsed = today.getTime() - startDate.getTime()
    const pct = (elapsed / total) * 100
    return Math.max(0, Math.min(100, pct))
  }

  const timeProgress = getTimeProgress()

  const isOverdue = deadline ? today > deadline && workProgress < 100 : false
  const daysRemaining = deadline
    ? Math.ceil((deadline.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
    : null

  // Compare work done vs time elapsed
  const diff = workProgress - timeProgress

  const getScheduleStatus = () => {
    if (!startDate || !deadline) return "No dates"
    if (isOverdue) return "Overdue"
    if (diff >= 10) return "Ahead of schedule"
    if (diff <= -10) return "Behind schedule"
    return "On track"
  }

  const getStatusColorScheme = () => {
    const status = getScheduleStatus()
    if (status === "Overdue" || status === "Behind schedule") return "red"
    if (status === "Ahead of schedule") return "green"
    if (status === "On track") return "blue"
    return "gray"
  }

  const getWorkColor = () => {
    const status = getScheduleStatus()
    if (status === "Overdue" || status === "Behind schedule") return "red.400"
    if (status === "Ahead of schedule") return "green.400"
    if (status === "On track") return "blue.400"
    return "gray.400"
  }

  const formatDate = (date: Date | null) =>
    date
      ? date.toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
          year: "numeric",
        })
      : "Not set"

  return (
    <Box w="100%">
      {/* Header */}
      <Flex justify="space-between" align="center" mb="4">
        <Box>
          <Text fontSize="lg" fontWeight="bold">
            Project Timeline
          </Text>
          <Text fontSize="sm" color="gray.500">
            {formatDate(startDate)} → {formatDate(deadline)}
          </Text>
        </Box>

        <Box textAlign="right">
          <Badge
            colorScheme={getStatusColorScheme()}
            borderRadius="full"
            px="3"
            py="1"
          >
            {getScheduleStatus()}
          </Badge>
          {daysRemaining !== null && (
            <Text fontSize="xs" color="gray.500" mt="1">
              {isOverdue
                ? `${Math.abs(daysRemaining)} days overdue`
                : `${daysRemaining} days remaining`}
            </Text>
          )}
          <Text fontSize="sm" mt="2">
            Work progress: <b>{Math.round(workProgress)}%</b>
          </Text>
        </Box>
      </Flex>

      {/* Timeline visual */}
      <Box mt="6" mb="4">
        <Box maxW="700px" mx="auto">
          <Box position="relative" h="32px">
            {/* Base track */}
            <Box
              position="absolute"
              top="50%"
              left="0"
              right="0"
              transform="translateY(-50%)"
              h="8px"
              bg="gray.100"
              borderRadius="full"
              overflow="hidden"
            >
              {/* Time elapsed bar (lighter, behind work) */}
              {startDate && deadline && (
                <Box
                  h="100%"
                  w={`${timeProgress}%`}
                  bg="gray.300"
                  borderRadius="full"
                />
              )}
            </Box>

            {/* Work progress bar (on top, more saturated) */}
            <Box
              position="absolute"
              top="50%"
              left="0"
              transform="translateY(-50%)"
              h="8px"
              w={`${workProgress}%`}
              bg={getWorkColor()}
              borderRadius="full"
              transition="width 0.25s ease-out"
            />

            {/* Today marker (vertical line at timeProgress) */}
            {startDate && deadline && (
              <Box
                position="absolute"
                top="0"
                left={`${timeProgress}%`}
                transform="translateX(-50%)"
                display="flex"
                flexDirection="column"
                alignItems="center"
                zIndex={2}
              >
                <Box w="2px" h="24px" bg="blue.500" borderRadius="full" />
                <Text
                  mt="1"
                  fontSize="xs"
                  fontWeight="medium"
                  color="blue.500"
                  whiteSpace="nowrap"
                >
                  Today
                </Text>
              </Box>
            )}
          </Box>

          {/* Start / deadline labels under the bar */}
          <Flex justify="space-between" mt="4" fontSize="xs" color="gray.600">
            <Box>
              <Text fontWeight="medium">Start</Text>
              <Text>{formatDate(startDate)}</Text>
            </Box>
            <Box textAlign="right">
              <Text fontWeight="medium">Deadline</Text>
              <Text>{formatDate(deadline)}</Text>
            </Box>
          </Flex>
        </Box>
      </Box>

      {/* Legend */}
      <Flex
        justify="center"
        gap="6"
        mt="4"
        fontSize="sm"
        color="gray.600"
        flexWrap="wrap"
      >
        <Flex align="center" gap="2">
          <Box w="12px" h="8px" bg={getWorkColor()} borderRadius="full" />
          <Text>Work completed</Text>
        </Flex>
        {startDate && deadline && (
          <Flex align="center" gap="2">
            <Box w="12px" h="8px" bg="gray.300" borderRadius="full" />
            <Text>Time elapsed</Text>
          </Flex>
        )}
        {startDate && deadline && (
          <Flex align="center" gap="2">
            <Box w="2px" h="12px" bg="blue.500" />
            <Text>Today (relative to deadline)</Text>
          </Flex>
        )}
      </Flex>
    </Box>
  )
}
