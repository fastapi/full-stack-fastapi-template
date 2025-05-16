import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"

import type { TicketPublic } from "@/client"
import DeleteTicket from "../Tickets/DeleteTicket"
import EditTicket from "../Tickets/EditTicket"
import ViewTicket from "../Tickets/ViewTicket"

interface TicketActionsMenuProps {
  ticket: TicketPublic
}

export const TicketActionsMenu = ({ ticket }: TicketActionsMenuProps) => {
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit">
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        <ViewTicket ticketId={ticket.id} />
        <EditTicket ticket={ticket} />
        <DeleteTicket id={ticket.id} />
      </MenuContent>
    </MenuRoot>
  )
}
