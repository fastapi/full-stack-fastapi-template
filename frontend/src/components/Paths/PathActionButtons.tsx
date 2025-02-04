import {
  Button,
  ButtonGroup,
  Icon,
  useDisclosure,
  AlertDialog,
  AlertDialogOverlay,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogBody,
  AlertDialogFooter,
} from "@chakra-ui/react"
import { useNavigate } from "@tanstack/react-router"
import { useQueryClient } from "@tanstack/react-query"
import { FaEdit, FaTrash } from "react-icons/fa"
import { useRef } from "react"
import { PathsService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"

interface PathActionButtonsProps {
  pathId: string
}

export default function PathActionButtons({ pathId }: PathActionButtonsProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const toast = useCustomToast()
  const { isOpen, onOpen, onClose } = useDisclosure()
  const cancelRef = useRef<HTMLButtonElement>(null)

  const handleEdit = () => {
    navigate({ to: `/paths/${pathId}` })
  }

  const handleDelete = async () => {
    try {
      await PathsService.deletePath({ pathId })
      queryClient.invalidateQueries({ queryKey: ["paths"] })
      toast("Success", "Path deleted successfully", "success")
      onClose()
    } catch (error) {
      toast(
        "Error",
        "Failed to delete path",
        "error"
      )
    }
  }

  return (
    <>
      <ButtonGroup size="sm" variant="ghost" spacing={1}>
        <Button
          onClick={handleEdit}
          aria-label="Edit path"
          leftIcon={<Icon as={FaEdit} />}
        >
          Edit
        </Button>
        <Button
          onClick={onOpen}
          aria-label="Delete path"
          leftIcon={<Icon as={FaTrash} />}
          colorScheme="red"
        >
          Delete
        </Button>
      </ButtonGroup>

      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete Path
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure? This action cannot be undone.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose}>
                Cancel
              </Button>
              <Button colorScheme="red" onClick={handleDelete} ml={3}>
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </>
  )
}