import { Textarea } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { FiMessageSquare } from "react-icons/fi"
import { Button } from "@/components/ui/button"
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

interface AddCommentProps {
  projectId: string
}

interface CommentFormData {
  content: string
}

export function AddComment({ projectId }: AddCommentProps) {
  const [open, setOpen] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CommentFormData>()

  const createMutation = useMutation({
    mutationFn: async (data: CommentFormData) => {
      const baseUrl = (
        import.meta.env.VITE_API_URL || "http://localhost:8000"
      ).replace(/\/$/, "")
      const response = await fetch(`${baseUrl}/api/v1/comments/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: data.content,
          project_id: projectId,
        }),
      })
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Failed to add comment")
      }
      return response.json()
    },
    onSuccess: () => {
      showSuccessToast("Comment added successfully")
      queryClient.invalidateQueries({
        queryKey: ["projectComments", projectId],
      })
      queryClient.invalidateQueries({ queryKey: ["project", projectId] })
      reset()
      setOpen(false)
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to add comment")
    },
  })

  const onSubmit = (data: CommentFormData) => {
    createMutation.mutate(data)
  }

  return (
    <DialogRoot open={open} onOpenChange={(e) => setOpen(e.open)}>
      <Button
        onClick={() => setOpen(true)}
        variant="ghost"
        width="full"
        justifyContent="flex-start"
      >
        <FiMessageSquare />
        Add Comment
      </Button>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Comment</DialogTitle>
        </DialogHeader>
        <DialogCloseTrigger />

        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogBody>
            <Field label="Comment" required invalid={!!errors.content}>
              <Textarea
                {...register("content", { required: "Comment is required" })}
                placeholder="Share your thoughts..."
                rows={5}
              />
            </Field>
          </DialogBody>

          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button
              type="submit"
              colorScheme="blue"
              loading={createMutation.isPending}
            >
              Post Comment
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </DialogRoot>
  )
}
