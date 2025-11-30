import { Text } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { FiTrash2 } from "react-icons/fi"
import { type ProjectPublic, ProjectsService } from "@/client"
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
import useCustomToast from "@/hooks/useCustomToast"

interface DeleteProjectProps {
  project: ProjectPublic
}

export function DeleteProject({ project }: DeleteProjectProps) {
  const [open, setOpen] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  const deleteMutation = useMutation({
    mutationFn: async () => {
      return await ProjectsService.deleteProject({ id: project.id })
    },
    onSuccess: () => {
      showSuccessToast("Project deleted successfully")
      queryClient.invalidateQueries({ queryKey: ["recentProjects"] })
      queryClient.invalidateQueries({ queryKey: ["dashboardStats"] })
      setOpen(false)
      // Navigate back to dashboard
      navigate({ to: "/dashboard" })
    },
    onError: (error: any) => {
      const message =
        error?.body?.detail || error?.message || "Failed to delete project"
      showErrorToast(message)
    },
  })

  const handleDelete = () => {
    deleteMutation.mutate()
  }

  return (
    <DialogRoot open={open} onOpenChange={(e) => setOpen(e.open)}>
      <Button onClick={() => setOpen(true)} colorScheme="red" variant="outline">
        <FiTrash2 />
        Delete Project
      </Button>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete Project</DialogTitle>
        </DialogHeader>
        <DialogCloseTrigger />

        <DialogBody>
          <Text>
            Are you sure you want to delete <strong>{project.name}</strong>?
            This action cannot be undone. All galleries and photos associated
            with this project will also be deleted.
          </Text>
        </DialogBody>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleDelete}
            colorScheme="red"
            loading={deleteMutation.isPending}
          >
            Delete Project
          </Button>
        </DialogFooter>
      </DialogContent>
    </DialogRoot>
  )
}
