import { Badge } from "@chakra-ui/react"
import { type TicketStatus } from "@/client"

interface TicketStatusBadgeProps {
  status: TicketStatus
}

const TicketStatusBadge = ({ status }: TicketStatusBadgeProps) => {
  let colorScheme = "blue"
  
  switch (status) {
    case "Aberto":
      colorScheme = "blue"
      break
    case "Em andamento":
      colorScheme = "orange"
      break
    case "Encerrado":
      colorScheme = "green"
      break
  }
  
  return (
    <Badge colorScheme={colorScheme} px={2} py={1} borderRadius="md">
      {status}
    </Badge>
  )
}

export default TicketStatusBadge
