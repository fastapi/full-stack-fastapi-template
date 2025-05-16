import { Badge } from "@chakra-ui/react"
import { type TicketPriority } from "@/client"

interface PriorityBadgeProps {
  priority: TicketPriority
}

const PriorityBadge = ({ priority }: PriorityBadgeProps) => {
  let colorScheme = "gray"
  
  switch (priority) {
    case "Baixa":
      colorScheme = "green"
      break
    case "Média":
      colorScheme = "yellow"
      break
    case "Alta":
      colorScheme = "red"
      break
  }
  
  return (
    <Badge colorScheme={colorScheme} px={2} py={1} borderRadius="md">
      {priority}
    </Badge>
  )
}

export default PriorityBadge
