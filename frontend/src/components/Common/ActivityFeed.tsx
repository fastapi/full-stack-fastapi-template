import { Box, Card, Flex, Heading, Stack, Text } from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import {
  FiImage,
  FiMessageSquare,
  FiCheckCircle,
  FiAlertCircle,
  FiUpload,
} from "react-icons/fi"

interface ActivityItem {
  id: string
  type: "comment" | "gallery_approved" | "gallery_changes" | "gallery_submitted" | "photo_upload"
  message: string
  timestamp: string
  projectId?: string
  projectName?: string
  userName?: string
}

export function ActivityFeed() {
  const { data: activities, isLoading } = useQuery({
    queryKey: ["activityFeed"],
    queryFn: async () => {
        const baseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "")
        
        const activities: ActivityItem[] = []
        
        try {
            // Fetch all projects to get recent activity
            const projectsRes = await fetch(`${baseUrl}/api/v1/projects/`, {
            headers: {
                Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
            })
            
            if (projectsRes.ok) {
            const projectsData = await projectsRes.json()
            const projects = projectsData.data || []
            
            // For each project, fetch its comments and galleries
            for (const project of projects.slice(0, 5)) { // Limit to 5 projects for performance
                // Fetch comments for this project
                try {
                const commentsRes = await fetch(`${baseUrl}/api/v1/comments/${project.id}`, {
                    headers: {
                    Authorization: `Bearer ${localStorage.getItem("access_token")}`,
                    },
                })
                
                if (commentsRes.ok) {
                    const commentsData = await commentsRes.json()
                    commentsData.data?.forEach((comment: any) => {
                    activities.push({
                        id: comment.id,
                        type: "comment",
                        message: `commented on ${project.name}: "${comment.content.substring(0, 40)}${comment.content.length > 40 ? "..." : ""}"`,
                        timestamp: comment.created_at,
                        projectId: comment.project_id,
                        projectName: project.name,
                        userName: comment.user?.full_name || comment.user?.email || "Someone",
                    })
                    })
                }
                } catch (e) {
                // Skip if comments fail
                }
                
                // Fetch galleries for this project
                try {
                const galleriesRes = await fetch(`${baseUrl}/api/v1/galleries/?project_id=${project.id}`, {
                    headers: {
                    Authorization: `Bearer ${localStorage.getItem("access_token")}`,
                    },
                })
                
                if (galleriesRes.ok) {
                    const galleriesData = await galleriesRes.json()
                    galleriesData.data?.forEach((gallery: any) => {
                    // Add activity for gallery status changes
                    if (gallery.status === "approved") {
                        activities.push({
                        id: gallery.id + "-approved",
                        type: "gallery_approved",
                        message: `approved gallery "${gallery.name}" in ${project.name}`,
                        timestamp: gallery.created_at, // Using created_at as proxy
                        projectId: project.id,
                        projectName: project.name,
                        userName: "Client",
                        })
                    } else if (gallery.status === "pending_review") {
                        activities.push({
                        id: gallery.id + "-submitted",
                        type: "gallery_submitted",
                        message: `submitted "${gallery.name}" for review in ${project.name}`,
                        timestamp: gallery.created_at,
                        projectId: project.id,
                        projectName: project.name,
                        userName: "Team",
                        })
                    } else if (gallery.status === "changes_requested") {
                        activities.push({
                        id: gallery.id + "-changes",
                        type: "gallery_changes",
                        message: `requested changes on "${gallery.name}" in ${project.name}`,
                        timestamp: gallery.created_at,
                        projectId: project.id,
                        projectName: project.name,
                        userName: "Client",
                        })
                    }
                    
                    // Add activity for photo uploads
                    if (gallery.photo_count > 0) {
                        activities.push({
                        id: gallery.id + "-photos",
                        type: "photo_upload",
                        message: `uploaded ${gallery.photo_count} photo${gallery.photo_count !== 1 ? "s" : ""} to "${gallery.name}"`,
                        timestamp: gallery.created_at,
                        projectId: project.id,
                        projectName: project.name,
                        userName: "Team",
                        })
                    }
                    })
                }
                } catch (e) {
                // Skip if galleries fail
                }
            }
            }
        } catch (error) {
            console.error("Failed to fetch activity:", error)
        }
        
        // Sort by timestamp (newest first)
        activities.sort((a, b) => 
            new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        )
        
        return activities.slice(0, 10)
        },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const getIcon = (type: string) => {
    switch (type) {
      case "comment":
        return <FiMessageSquare />
      case "gallery_approved":
        return <FiCheckCircle color="green" />
      case "gallery_changes":
        return <FiAlertCircle color="orange" />
      case "gallery_submitted":
        return <FiUpload color="blue" />
      case "photo_upload":
        return <FiImage />
      default:
        return <FiMessageSquare />
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp + "Z")
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return "Just now"
    if (diffMins < 60) return `${diffMins} min${diffMins !== 1 ? "s" : ""} ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? "s" : ""} ago`
    if (diffDays < 7) return `${diffDays} day${diffDays !== 1 ? "s" : ""} ago`
    return date.toLocaleDateString()
  }

  if (isLoading) {
    return (
      <Card.Root bg="white" borderColor="#E2E8F0">
        <Card.Header>
          <Heading size="lg" color="#1E3A8A">Recent Activity</Heading>
        </Card.Header>
        <Card.Body>
          <Text color="#64748B">Loading activity...</Text>
        </Card.Body>
      </Card.Root>
    )
  }

  const items = activities || []

  return (
    <Card.Root bg="white" borderColor="#E2E8F0">
      <Card.Header>
        <Heading size="lg" color="#1E3A8A">Recent Activity</Heading>
      </Card.Header>
      <Card.Body>
        {items.length === 0 ? (
          <Text color="#64748B">No recent activity</Text>
        ) : (
          <Stack gap={3}>
            {items.map((activity) => (
              <Flex
                key={activity.id}
                gap={3}
                p={3}
                borderRadius="md"
                borderWidth="1px"
                borderColor="#E2E8F0"
                bg="white"
                alignItems="start"
                _hover={{ bg: "#F8FAFC" }}
              >
                <Box mt={1} color="#1E3A8A">{getIcon(activity.type)}</Box>
                <Box flex={1}>
                  <Text fontSize="sm" color="#1E293B">
                    <strong>{activity.userName || "Someone"}</strong> {activity.message}
                  </Text>
                  <Text fontSize="xs" color="#64748B" mt={1}>
                    {formatTimestamp(activity.timestamp)}
                  </Text>
                </Box>
              </Flex>
            ))}
          </Stack>
        )}
      </Card.Body>
    </Card.Root>
  )
}