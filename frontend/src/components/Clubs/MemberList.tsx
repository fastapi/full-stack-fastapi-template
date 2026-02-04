import { useMutation, useQueryClient } from "@tanstack/react-query"
import { MoreHorizontal, UserMinus } from "lucide-react"

import type { ClubMemberWithUser } from "@/client"
import { ClubsService } from "@/client"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { MemberRoleBadge } from "./MemberRoleBadge"

interface MemberListProps {
  clubId: string
  members: ClubMemberWithUser[]
  currentUserRole?: string
}

export function MemberList({ clubId, members, currentUserRole }: MemberListProps) {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const isOwner = currentUserRole === "owner"
  const isAdmin = currentUserRole === "admin" || isOwner

  const removeMemberMutation = useMutation({
    mutationFn: (userId: string) =>
      ClubsService.removeMember({ clubId, userId }),
    onSuccess: () => {
      showSuccessToast("Member removed")
      queryClient.invalidateQueries({ queryKey: ["clubs", clubId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const updateRoleMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: string }) =>
      ClubsService.updateMemberRole({ clubId, userId, role: role as any }),
    onSuccess: () => {
      showSuccessToast("Role updated")
      queryClient.invalidateQueries({ queryKey: ["clubs", clubId] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const getInitials = (name: string | null | undefined, email: string) => {
    if (name) {
      return name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    }
    return email.slice(0, 2).toUpperCase()
  }

  return (
    <div className="space-y-2">
      <h3 className="font-semibold">Members ({members.length})</h3>
      <div className="space-y-2">
        {members.map((member) => {
          const canManage =
            isAdmin &&
            member.user_id !== user?.id &&
            member.role !== "owner" &&
            (isOwner || member.role !== "admin")

          return (
            <div
              key={member.id}
              className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
            >
              <div className="flex items-center gap-3">
                <Avatar className="h-10 w-10">
                  <AvatarFallback>
                    {getInitials(member.user.full_name, member.user.email)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium">
                    {member.user.full_name || member.user.email}
                  </p>
                  {member.user.full_name && (
                    <p className="text-sm text-muted-foreground">
                      {member.user.email}
                    </p>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <MemberRoleBadge role={member.role ?? "member"} />
                {canManage && (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      {member.role === "pending" && (
                        <DropdownMenuItem
                          onClick={() =>
                            updateRoleMutation.mutate({
                              userId: member.user_id,
                              role: "member",
                            })
                          }
                        >
                          Approve
                        </DropdownMenuItem>
                      )}
                      {member.role === "member" && isOwner && (
                        <DropdownMenuItem
                          onClick={() =>
                            updateRoleMutation.mutate({
                              userId: member.user_id,
                              role: "admin",
                            })
                          }
                        >
                          Promote to Admin
                        </DropdownMenuItem>
                      )}
                      {member.role === "admin" && isOwner && (
                        <DropdownMenuItem
                          onClick={() =>
                            updateRoleMutation.mutate({
                              userId: member.user_id,
                              role: "member",
                            })
                          }
                        >
                          Demote to Member
                        </DropdownMenuItem>
                      )}
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        className="text-destructive"
                        onClick={() => removeMemberMutation.mutate(member.user_id)}
                      >
                        <UserMinus className="h-4 w-4 mr-2" />
                        Remove
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
