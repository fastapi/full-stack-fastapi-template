import { Button } from "@/components/ui/button"
import {
  DialogBackdrop,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "@/components/ui/dialog"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"

import { ItemsService, UsersService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"

interface DeleteProps {
  type: string
  id: string
  open: boolean
  onClose: () => void
}

const Delete = ({ type, id, open, onClose }: DeleteProps) => {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = useForm()

  const deleteEntity = async (id: string) => {
    if (type === "Item") {
      await ItemsService.deleteItem({ id })
    } else if (type === "User") {
      await UsersService.deleteUser({ id })
    } else {
      throw new Error(`Unexpected type: ${type}`)
    }
  }

  const mutation = useMutation({
    mutationFn: deleteEntity,
    onSuccess: () => {
      showSuccessToast(`The ${type.toLowerCase()} was deleted successfully.`)
      onClose()
    },
    onError: () => {
      showErrorToast(
        `An error occurred while deleting the ${type.toLowerCase()}.`,
      )
    },
    onSettled: () => {
      queryClient.invalidateQueries({
        queryKey: [type === "Item" ? "items" : "users"],
      })
    },
  })

  const onSubmit = async () => {
    mutation.mutate(id)
  }

  return (
    <>
      <DialogRoot
        open={open}
        onExitComplete={onClose}
        size={{ base: "sm", md: "md" }}
        role="alertdialog"
      >
        <DialogBackdrop />
        <DialogContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Delete {type}</DialogTitle>
            <DialogCloseTrigger />
          </DialogHeader>

          <DialogBody>
            {type === "User" && (
              <span>
                All items associated with this user will also be{" "}
                <strong>permantly deleted. </strong>
              </span>
            )}
            Are you sure? You will not be able to undo this action.
          </DialogBody>

          <DialogFooter gap={3}>
            <Button colorPalette="red" type="submit" loading={isSubmitting}>
              Delete
            </Button>
            <Button onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
          </DialogFooter>
        </DialogContent>
      </DialogRoot>
    </>
  )
}

export default Delete
