import { Button, Icon } from "@chakra-ui/react"
import { useNavigate } from "@tanstack/react-router"
import { FaPlus } from "react-icons/fa"

export default function AddPathButton() {
  const navigate = useNavigate()

  return (
    <Button
      variant="primary"
      gap={1}
      fontSize={{ base: "sm", md: "inherit" }}
      onClick={() => navigate({ to: "/paths/create" })}
    >
      <Icon as={FaPlus} /> Add Path
    </Button>
  )
}
