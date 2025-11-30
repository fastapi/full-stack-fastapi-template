import { Box, Card, Flex, Heading, Stack, Text } from "@chakra-ui/react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { FiMessageSquare, FiUser, FiTrash2 } from "react-icons/fi"
import { Button } from "@/components/ui/button"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"

interface CommentsListProps {
  projectId: string
}

export function CommentsList({ projectId }: CommentsListProps) {
  const { user: currentUser } = useAuth()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const { data: commentsData, isLoading } = useQuery({
    queryKey: ["projectComments", projectId],
    queryFn: async () => {
      const baseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "")
      const response = await fetch(`${baseUrl}/api/v1/comments/${projectId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      })
      if (!response.ok) return { data: [], count: 0 }
      return response.json()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (commentId: string) => {
      const baseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "")
      const response = await fetch(`${baseUrl}/api/v1/comments/${commentId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      })
      if (!response.ok) throw new Error("Failed to delete comment")
      return response.json()
    },
    onSuccess: () => {
      showSuccessToast("Comment deleted")
      queryClient.invalidateQueries({ queryKey: ["projectComments", projectId] })
    },
    onError: () => {
      showErrorToast("Failed to delete comment")
    },
  })

  const comments = commentsData?.data || []

  if (isLoading) {
    return (
      <Card.Root>
        <Card.Header>
          <Heading size="lg">Comments</Heading>
        </Card.Header>
        <Card.Body>
          <Text>Loading comments...</Text>
        </Card.Body>
      </Card.Root>
    )
  }

  return (
    <Card.Root>
      <Card.Header>
        <Flex justify="space-between" align="center">
          <Heading size="lg">Comments</Heading>
          <Flex align="center" gap={2}>
            <FiMessageSquare />
            <Text fontSize="sm" color="fg.muted">{comments.length} comments</Text>
          </Flex>
        </Flex>
      </Card.Header>
      <Card.Body>
        {comments.length === 0 ? (
          <Text color="fg.muted">No comments yet. Be the first to comment!</Text>
        ) : (
          <Stack gap={4}>
            {comments.map((comment: any) => (
              <Box
                key={comment.id}
                p={4}
                borderWidth="1px"
                borderRadius="md"
                bg="bg.subtle"
              >
                <Flex gap={3}>
                  <Box>
                    <FiUser size={20} />
                  </Box>
                  <Box flex={1}>
                    <Flex justify="space-between" align="center" mb={2}>
                      <Text fontWeight="semibold" fontSize="sm">
                        {comment.user?.full_name || comment.user?.email || "Unknown User"}
                      </Text>
                      <Flex align="center" gap={2}>
                        <Text fontSize="xs" color="fg.muted">
                          {new Date(comment.created_at + "Z").toLocaleString("en-US", {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </Text>
                        {currentUser?.id === comment.user_id && (
                          <Button
                            size="xs"
                            variant="ghost"
                            colorScheme="red"
                            onClick={() => deleteMutation.mutate(comment.id)}
                            loading={deleteMutation.isPending}
                          >
                            <FiTrash2 size={14} />
                          </Button>
                        )}
                      </Flex>
                    </Flex>
                    <Text fontSize="sm">{comment.content}</Text>
                  </Box>
                </Flex>
              </Box>
            ))}
          </Stack>
        )}
      </Card.Body>
    </Card.Root>
  )
}