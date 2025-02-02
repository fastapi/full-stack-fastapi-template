import {
  AlertDialog,
  AlertDialogBody,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogOverlay,
  Button,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import React from "react"
import { useForm } from "react-hook-form"

import { ItemsService, UsersService, PathsService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"

interface DeleteProps {
  type: string
  id: string
  isOpen: boolean
  onClose: () => void
}

const Delete = ({ type, id, isOpen, onClose }: DeleteProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const cancelRef = React.useRef<HTMLButtonElement | null>(null)
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = useForm()

  const deleteEntity = async (id: string) => {
    if (type === "Item") {
      await ItemsService.deleteItem({ id: id })
    } else if (type === "User") {
      await UsersService.deleteUser({ userId: id })
    } else if (type === "Path") {
      await PathsService.deletePath({ pathId: id })
    } else {
      throw new Error(`Unexpected type: ${type}`)
    }
  }

  const mutation = useMutation({
    mutationFn: () => deleteEntity(id),
    onSuccess: () => {
      showToast(
        "Success",
        `The ${type.toLowerCase()} was deleted successfully.`,
        "success",
      )
      // Invalidate the correct query based on type
      if (type === "Path") {
        queryClient.invalidateQueries({ queryKey: ["paths"] })
      } else if (type === "Item") {
        queryClient.invalidateQueries({ queryKey: ["items"] })
      } else if (type === "User") {
        queryClient.invalidateQueries({ queryKey: ["users"] })
      }
      onClose()
    },
    onError: () => {
      showToast(
        "An error occurred",
        `An error occurred while deleting the ${type.toLowerCase()}.`,
        "error",
      )
    },
  })

  const onSubmit = handleSubmit(() => {
    mutation.mutate()
  })

  return (
    <>
      <AlertDialog
        isOpen={isOpen}
        onClose={onClose}
        leastDestructiveRef={cancelRef}
        size={{ base: "sm", md: "md" }}
        isCentered
      >
        <AlertDialogOverlay>
          <AlertDialogContent as="form" onSubmit={onSubmit}>
            <AlertDialogHeader>Delete {type}</AlertDialogHeader>

            <AlertDialogBody>
              {type === "User" && (
                <span>
                  All items associated with this user will also be{" "}
                  <strong>permantly deleted. </strong>
                </span>
              )}
              Are you sure? You will not be able to undo this action.
            </AlertDialogBody>

            <AlertDialogFooter gap={3}>
              <Button variant="danger" type="submit" isLoading={isSubmitting}>
                Delete
              </Button>
              <Button
                ref={cancelRef}
                onClick={onClose}
                isDisabled={isSubmitting}
              >
                Cancel
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </>
  )
}

export default Delete
