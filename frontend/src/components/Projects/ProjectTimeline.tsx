import { Box, Text, Flex, Badge } from "@chakra-ui/react"
import { type ProjectPublic } from "@/client"

interface ProjectTimelineProps {
  project: ProjectPublic
}

export function ProjectTimeline({ project }: ProjectTimelineProps) {
  const startDate = project.start_date ? new Date(project.start_date) : null
  const deadline = project.deadline ? new Date(project.deadline) : null
  const today = new Date()
  
  // Calculate progress based on dates
  const getDateProgress = () => {
    if (!startDate || !deadline) return 0
    const total = deadline.getTime() - startDate.getTime()
    const elapsed = today.getTime() - startDate.getTime()
    return Math.max(0, Math.min(100, (elapsed / total) * 100))
  }

  const dateProgress = getDateProgress()
  const isOverdue = deadline && today > deadline
  const daysRemaining = deadline 
    ? Math.ceil((deadline.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
    : null

  // Define milestones based on project phases
  const milestones = [
    { label: "Start", date: startDate, position: 0 },
    { label: "25%", date: null, position: 25 },
    { label: "50%", date: null, position: 50 },
    { label: "75%", date: null, position: 75 },
    { label: "Deadline", date: deadline, position: 100 },
  ]

  const getStatusColor = () => {
    if (isOverdue) return "red.500"
    if (dateProgress > 75) return "orange.500"
    if (dateProgress > 50) return "yellow.500"
    return "green.500"
  }

  const formatDate = (date: Date | null) => {
    if (!date) return "Not set"
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
  }

  return (
    <Box width="100%">
      {/* Header */}
      <Flex justify="space-between" align="center" mb="6">
        <Box>
          <Text fontSize="lg" fontWeight="bold">Project Timeline</Text>
          <Text fontSize="sm" color="fg.muted">
            {formatDate(startDate)} → {formatDate(deadline)}
          </Text>
        </Box>
        <Box textAlign="right">
          {daysRemaining !== null && (
            <Badge colorScheme={isOverdue ? "red" : daysRemaining < 7 ? "orange" : "green"}>
              {isOverdue ? `${Math.abs(daysRemaining)} days overdue` : `${daysRemaining} days left`}
            </Badge>
          )}
          <Text fontSize="sm" color="fg.muted" mt="1">
            Progress: {project.progress || 0}%
          </Text>
        </Box>
      </Flex>

      {/* Timeline */}
      <Box position="relative" mt="16" mb="16" px="4">
        {/* Background track */}
        <Box
          position="absolute"
          top="40px"
          left="4"
          right="4"
          height="8px"
          bg="bg.muted"
          borderRadius="full"
        />

        {/* Progress bar (based on actual progress) */}
        <Box
          position="absolute"
          top="40px"
          left="-6"
          width={`calc(${project.progress || 0}% - -16px)`}
          height="8px"
          bg={getStatusColor()}
          borderRadius="full"
          transition="width 0.3s ease"
        />

        {/* Current date indicator (based on time elapsed) */}
        {startDate && deadline && (
          <Box
            position="absolute"
            top="24px"
            left={`calc(${dateProgress}%)`}
            transform="translateX(-75%)"
            zIndex="3"
          >
            <Box
              width="2px"
              height="24px"
              bg="blue.500"
              mb="4"
            />
            <Text
              fontSize="xs"
              fontWeight="bold"
              color="blue.500"
              textAlign="center"
              whiteSpace="nowrap"
              mt="-1"
            >
              Today
            </Text>
          </Box>
        )}

        {/* Milestones */}
        {milestones.map((milestone, index) => (
          <Box
            key={index}
            position="absolute"
            top="36px"
            left={`${milestone.position}%`}
            transform="translateX(-30%)"
            zIndex="2"
          >
            {/* Milestone dot */}
            <Box
              width="16px"
              height="16px"
              bg={milestone.position <= (project.progress || 0) ? getStatusColor() : "bg.muted"}
              borderRadius="full"
              borderWidth="3px"
              borderColor="white"
              boxShadow="sm"
            />
            
            {/* Milestone label */}
            <Text
              fontSize="xs"
              color="fg.muted"
              textAlign="center"
              whiteSpace="nowrap"
              mt="6"
            >
              {milestone.label}
            </Text>
            
            {/* Date if available */}
            {milestone.date && (
              <Text
                fontSize="xs"
                color="fg.subtle"
                textAlign="center"
                whiteSpace="nowrap"
                mt="1"
              >
                {formatDate(milestone.date)}
              </Text>
            )}
          </Box>
        ))}
      </Box>

      {/* Status legend */}
      <Flex gap="4" mt="8" fontSize="sm" color="fg.muted" justify="center">
        <Flex align="center" gap="2">
          <Box width="12px" height="12px" bg={getStatusColor()} borderRadius="full" />
          <Text>Current Progress</Text>
        </Flex>
        <Flex align="center" gap="2">
          <Box width="12px" height="12px" bg="blue.500" borderRadius="full" />
          <Text>Today</Text>
        </Flex>
      </Flex>
    </Box>
  )
}