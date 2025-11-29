import { useState } from "react"
import { useForm } from "react-hook-form"
import {
  DialogRoot,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogBody,
  DialogFooter,
  DialogCloseTrigger,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Field } from "@/components/ui/field"
import { Input, Textarea, NativeSelectRoot, NativeSelectField } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { ProjectsService, type ProjectCreate } from "@/client"
import { FiPlus } from "react-icons/fi"
import useCustomToast from "@/hooks/useCustomToast"
import useAuth from "@/hooks/useAuth"

export function CreateProject() {
  const [open, setOpen] = useState(false)
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const { user: currentUser } = useAuth()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ProjectCreate>({
    defaultValues: {
      name: "",
      description: "",
      client_name: "",
      client_email: "",
      status: "planning",
      budget: "",
      start_date: "",
      deadline: "",
      progress: 0,
      organization_id: currentUser?.organization_id || "",
    },
  })

  const createMutation = useMutation({
    mutationFn: async (data: ProjectCreate) => {
      if (!currentUser?.organization_id) {
        throw new Error("No organization assigned. Please contact support.")
      }
      
      return await ProjectsService.createProject({
        requestBody: {
          ...data,
          organization_id: currentUser.organization_id,
        },
      })
    },
    onSuccess: () => {
      showSuccessToast("Project created successfully")
      queryClient.invalidateQueries({ queryKey: ["recentProjects"] })
      queryClient.invalidateQueries({ queryKey: ["dashboardStats"] })
      // Also refresh projects list so the new project appears immediately
      queryClient.invalidateQueries({ queryKey: ["projects"] })
      setOpen(false)
      reset()
    },
    onError: (error: any) => {
      let message = "Failed to create project"
      
      if (error?.body?.detail) {
        if (Array.isArray(error.body.detail)) {
          // Handle validation errors (422)
          message = error.body.detail.map((e: any) => e.msg).join(", ")
        } else if (typeof error.body.detail === "string") {
          message = error.body.detail
        }
      } else if (error?.message) {
        message = error.message
      }
      
      showErrorToast(message)
    },
  })

  const onSubmit = (data: ProjectCreate) => {
    // Clean up empty strings to undefined for optional fields
    const cleanData = {
      ...data,
      description: data.description || undefined,
      client_email: data.client_email || undefined,
      budget: data.budget || undefined,
      start_date: data.start_date || undefined,
      deadline: data.deadline || undefined,
    }
    createMutation.mutate(cleanData)
  }

  return (
    <DialogRoot open={open} onOpenChange={(e) => setOpen(e.open)} size="lg">
      <Button
        onClick={() => setOpen(true)}
        colorScheme="blue"
      >
        <FiPlus />
        New Project
      </Button>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New Project</DialogTitle>
        </DialogHeader>
        <DialogCloseTrigger />

        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogBody>
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              <Field label="Project Name" required invalid={!!errors.name}>
                <Input
                  {...register("name", { required: "Project name is required" })}
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

              <Field label="Client Name" required invalid={!!errors.client_name}>
                <Input
                  {...register("client_name", { required: "Client name is required" })}
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
                <Input
                  {...register("budget")}
                  placeholder="e.g. $5,000"
                />
              </Field>

              <Field label="Start Date">
                <Input
                  {...register("start_date")}
                  type="date"
                />
              </Field>

              <Field label="Deadline">
                <Input
                  {...register("deadline")}
                  type="date"
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
              loading={createMutation.isPending}
            >
              Create Project
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </DialogRoot>
  )
}

