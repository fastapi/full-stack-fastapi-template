import {
  Input,
  NativeSelectField,
  NativeSelectRoot,
  Textarea,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { FiEdit } from "react-icons/fi"
import {
  type ProjectPublic,
  ProjectsService,
  type ProjectUpdate,
} from "@/client"
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

interface EditProjectProps {
  project: ProjectPublic
}

export function EditProject({ project }: EditProjectProps) {
  const [open, setOpen] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProjectUpdate>({
    defaultValues: {
      name: project.name,
      description: project.description || "",
      client_name: project.client_name,
      client_email: project.client_email || "",
      status: project.status || "planning",
      budget: project.budget || "",
      start_date: project.start_date || "",
      deadline: project.deadline || "",
      progress: project.progress || 0,
    },
  })

  const updateMutation = useMutation({
    mutationFn: async (data: ProjectUpdate) => {
      return await ProjectsService.updateProject({
        id: project.id,
        requestBody: data,
      })
    },
    onSuccess: () => {
      showSuccessToast("Project updated successfully")
      queryClient.invalidateQueries({ queryKey: ["project", project.id] })
      queryClient.invalidateQueries({ queryKey: ["recentProjects"] })
      queryClient.invalidateQueries({ queryKey: ["dashboardStats"] })
      setOpen(false)
    },
    onError: (error: any) => {
      const message =
        error?.body?.detail || error?.message || "Failed to update project"
      showErrorToast(message)
    },
  })

  const onSubmit = (data: ProjectUpdate) => {
    updateMutation.mutate(data)
  }

  return (
    <DialogRoot open={open} onOpenChange={(e) => setOpen(e.open)} size="lg">
      <Button
        onClick={() => setOpen(true)}
        colorScheme="blue"
        variant="outline"
      >
        <FiEdit />
        Manage Project
      </Button>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Manage Project</DialogTitle>
        </DialogHeader>
        <DialogCloseTrigger />

        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogBody>
            <div
              style={{ display: "flex", flexDirection: "column", gap: "16px" }}
            >
              <Field label="Project Name" required invalid={!!errors.name}>
                <Input
                  {...register("name", {
                    required: "Project name is required",
                  })}
                  placeholder="Enter project name"
                />
              </Field>

              <Field label="Description">
                <Textarea
                  {...register("description")}
                  placeholder="Project description"
                  rows={3}
                />
              </Field>

              <Field
                label="Client Name"
                required
                invalid={!!errors.client_name}
              >
                <Input
                  {...register("client_name", {
                    required: "Client name is required",
                  })}
                  placeholder="Enter client name"
                />
              </Field>

              <Field label="Client Email">
                <Input
                  {...register("client_email")}
                  type="email"
                  placeholder="client@example.com"
                />
              </Field>

              <Field label="Status">
                <NativeSelectRoot>
                  <NativeSelectField {...register("status")}>
                    <option value="planning">Planning</option>
                    <option value="in_progress">In Progress</option>
                    <option value="review">Review</option>
                    <option value="completed">Completed</option>
                    <option value="pending">Pending</option>
                  </NativeSelectField>
                </NativeSelectRoot>
              </Field>

              <Field label="Budget">
                <Input {...register("budget")} placeholder="e.g. $5,000" />
              </Field>

              <Field label="Start Date">
                <Input {...register("start_date")} type="date" />
              </Field>

              <Field label="Deadline">
                <Input {...register("deadline")} type="date" />
              </Field>

              <Field label="Progress (%)">
                <Input
                  {...register("progress", {
                    valueAsNumber: true,
                    min: 0,
                    max: 100,
                  })}
                  type="number"
                  min="0"
                  max="100"
                />
              </Field>
            </div>
          </DialogBody>

          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button
              type="submit"
              colorScheme="blue"
              loading={updateMutation.isPending}
            >
              Save Changes
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </DialogRoot>
  )
}
