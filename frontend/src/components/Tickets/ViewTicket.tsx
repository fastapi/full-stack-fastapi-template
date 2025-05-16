import {
  Box,
  Button,
  DialogTitle,
  Flex,
  Heading,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { format } from "date-fns"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FiEye } from "react-icons/fi"

import { CommentsService, TicketsService, type CommentCreate } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog"

interface ViewTicketProps {
  ticketId: string
}

const ViewTicket = ({ ticketId }: ViewTicketProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const { data: ticket, isLoading } = useQuery({
    queryKey: ["ticket", ticketId],
    queryFn: () => TicketsService.readTicket({ id: ticketId }),
    enabled: isOpen,
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CommentCreate>({
    defaultValues: {
      content: "",
    },
  })

  const addCommentMutation = useMutation({
    mutationFn: (data: CommentCreate) =>
      CommentsService.createComment({
        ticket_id: ticketId,
        requestBody: data,
      }),
    onSuccess: () => {
      showSuccessToast("Comment added successfully")
      reset()
      queryClient.invalidateQueries({ queryKey: ["ticket", ticketId] })
    },
    onError: () => {
      showErrorToast("Error adding comment")
    },
  })

  const onSubmit: SubmitHandler<CommentCreate> = (data) => {
    addCommentMutation.mutate(data)
  }

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), "PPpp")
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "lg" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost">
          <FiEye fontSize="16px" />
          View Details
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Ticket Details</DialogTitle>
        </DialogHeader>
        <DialogBody maxH="70vh" overflow="auto">
          {isLoading ? (
            <Text>Loading...</Text>
          ) : ticket ? (
            <VStack align="stretch" gap={4}>
              <Box>
                <Heading size="md">{ticket.title}</Heading>
                <Flex gap={2} mt={2} fontSize="sm" color="gray.500">
                  <Text>Category: {ticket.category}</Text>
                  <Text>•</Text>
                  <Text>Priority: {ticket.priority}</Text>
                  <Text>•</Text>
                  <Text>Status: {ticket.status}</Text>
                </Flex>
                <Text mt={2} fontSize="sm" color="gray.500">
                  Created: {formatDate(ticket.created_at)}
                </Text>
                <Text mt={2} fontSize="sm" color="gray.500">
                  Updated: {formatDate(ticket.updated_at)}
                </Text>
              </Box>

              <Box bg="gray.50" p={4} borderRadius="md">
                <Text whiteSpace="pre-wrap">{ticket.description}</Text>
              </Box>

              <Box my={2} height="1px" bg="gray.200" />

              <Heading size="sm" mt={4}>
                Comments ({ticket.comments.length})
              </Heading>

              {ticket.comments.length > 0 ? (
                <VStack align="stretch" gap={4} mt={2}>
                  {ticket.comments.map((comment) => (
                    <Box
                      key={comment.id}
                      bg="gray.50"
                      p={4}
                      borderRadius="md"
                      borderLeft="4px solid"
                      borderLeftColor="blue.400"
                    >
                      <Text fontSize="xs" color="gray.500" mb={1}>
                        {formatDate(comment.created_at)}
                      </Text>
                      <Text>{comment.content}</Text>
                    </Box>
                  ))}
                </VStack>
              ) : (
                <Text color="gray.500">No comments yet</Text>
              )}

              <Box my={2} height="1px" bg="gray.200" />

              <form onSubmit={handleSubmit(onSubmit)}>
                <Box mb={4}>
                  <label
                    htmlFor="content"
                    style={{
                      fontWeight: "500",
                      marginBottom: "0.25rem",
                      display: "block",
                    }}
                  >
                    Add a comment
                  </label>
                  <Input
                    id="content"
                    {...register("content", {
                      required: "Comment text is required",
                    })}
                    placeholder="Write your comment here"
                  />
                  {errors.content && (
                    <Text color="red.500" fontSize="sm" mt={1}>
                      {errors.content.message}
                    </Text>
                  )}
                </Box>
                <Button
                  mt={4}
                  colorPalette="blue"
                  type="submit"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Adding..." : "Add Comment"}
                </Button>
              </form>
            </VStack>
          ) : (
            <Text>Ticket not found</Text>
          )}
        </DialogBody>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default ViewTicket
