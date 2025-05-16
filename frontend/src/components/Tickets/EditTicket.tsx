import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Input,
  Text,
  Textarea,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaExchangeAlt } from "react-icons/fa"

import { 
  type ApiError, 
  type TicketPublic, 
  type TicketUpdate, 
  TicketsService 
} from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface EditTicketProps {
  ticket: TicketPublic
}

const EditTicket = ({ ticket }: EditTicketProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TicketUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      ...ticket,
      description: ticket.description ?? undefined,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: TicketUpdate) =>
      TicketsService.updateTicket({ id: ticket.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Ticket updated successfully.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["tickets"] })
    },
  })

  const onSubmit: SubmitHandler<TicketUpdate> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost">
          <FaExchangeAlt fontSize="16px" />
          Edit Ticket
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Edit Ticket</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Update the ticket details below.</Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.title}
                errorText={errors.title?.message}
                label="Title"
              >
                <Input
                  id="title"
                  {...register("title")}
                  placeholder="Title"
                  type="text"
                />
              </Field>

              <Field
                invalid={!!errors.description}
                errorText={errors.description?.message}
                label="Description"
              >
                <Textarea
                  id="description"
                  {...register("description")}
                  placeholder="Description"
                  rows={4}
                />
              </Field>

              <Field
                required
                invalid={!!errors.category}
                errorText={errors.category?.message}
                label="Category"
              >
                <select
                  id="category"
                  className="chakra-select"
                  {...register("category")}
                >
                  <option value="Suporte">Support</option>
                  <option value="Manutenção">Maintenance</option>
                  <option value="Dúvida">Question</option>
                </select>
              </Field>

              <Field
                required
                invalid={!!errors.priority}
                errorText={errors.priority?.message}
                label="Priority"
              >
                <select
                  id="priority"
                  className="chakra-select"
                  {...register("priority")}
                >
                  <option value="Baixa">Low</option>
                  <option value="Média">Medium</option>
                  <option value="Alta">High</option>
                </select>
              </Field>

              <Field
                required
                invalid={!!errors.status}
                errorText={errors.status?.message}
                label="Status"
              >
                <select
                  id="status"
                  className="chakra-select"
                  {...register("status")}
                >
                  <option value="Aberto">Open</option>
                  <option value="Em andamento">In Progress</option>
                  <option value="Encerrado">Closed</option>
                </select>
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
              </DialogActionTrigger>
              <Button variant="solid" type="submit" loading={isSubmitting}>
                Save
              </Button>
            </ButtonGroup>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default EditTicket
