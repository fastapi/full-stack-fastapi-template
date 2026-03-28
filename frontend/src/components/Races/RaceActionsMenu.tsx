import { Link as RouterLink } from "@tanstack/react-router"
import { Edit, MoreVertical, Trash } from "lucide-react"

import type { RacePublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteRace from "./DeleteRace"

interface RaceActionsMenuProps {
  race: RacePublic
}

export function RaceActionsMenu({ race }: RaceActionsMenuProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <MoreVertical className="h-4 w-4" />
          <span className="sr-only">Open menu</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>Actions</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <RouterLink to="/admin/races/$raceId/edit" params={{ raceId: race.id }}>
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </RouterLink>
        </DropdownMenuItem>
        <DeleteRace race={race}>
          <DropdownMenuItem
            onSelect={(e) => e.preventDefault()}
            className="text-destructive focus:text-destructive"
          >
            <Trash className="mr-2 h-4 w-4" />
            Delete
          </DropdownMenuItem>
        </DeleteRace>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
