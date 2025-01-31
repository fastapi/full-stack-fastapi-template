import { useNavigate } from "@tanstack/react-router"

interface AddPathButtonProps {
  isOpen: boolean
  onClose: () => void
}

export default function AddPathButton({ isOpen, onClose }: AddPathButtonProps) {
  const navigate = useNavigate()

  // Redirect to create page when "opened"
  if (isOpen) {
    navigate({ to: "/paths/create" })
    onClose()
  }

  return null
}
