import { EllipsisVertical } from "lucide-react"
import { useState } from "react"

import type { UserPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import useAuth from "@/hooks/useAuth"
import usePermissions from "@/hooks/usePermissions"
import DeleteUser from "./DeleteUser"
import EditUser from "./EditUser"

interface UserActionsMenuProps {
  user: UserPublic
}

export const UserActionsMenu = ({ user }: UserActionsMenuProps) => {
  const [open, setOpen] = useState(false)
  const { user: currentUser } = useAuth()
  const { can } = usePermissions()

  if (user.id === currentUser?.id) {
    return null
  }

  if (!can("users:update_any") && !can("users:delete")) {
    return null
  }

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {can("users:update_any") ? (
          <EditUser user={user} onSuccess={() => setOpen(false)} />
        ) : null}
        {can("users:delete") ? (
          <DeleteUser id={user.id} onSuccess={() => setOpen(false)} />
        ) : null}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
