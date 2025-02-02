import { Button, ButtonGroup, Icon } from "@chakra-ui/react"
import { useNavigate } from "@tanstack/react-router"
import { FaEdit, FaTrash } from "react-icons/fa"

interface PathActionButtonsProps {
  pathId: string
}

export default function PathActionButtons({ pathId }: PathActionButtonsProps) {
  const navigate = useNavigate()

  const handleEdit = () => {
    navigate({ to: `/paths/${pathId}` })
  }

  const handleDelete = () => {
    // TODO: Implement delete functionality
    console.log('Delete path:', pathId)
  }

  return (
    <ButtonGroup size="sm" variant="ghost" spacing={1}>
      <Button
        onClick={handleEdit}
        aria-label="Edit path"
        leftIcon={<Icon as={FaEdit} />}
      >
        Edit
      </Button>
      <Button
        onClick={handleDelete}
        aria-label="Delete path"
        leftIcon={<Icon as={FaTrash} />}
        colorScheme="red"
      >
        Delete
      </Button>
    </ButtonGroup>
  )
}