import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { Globe, Lock, LogOut, Trash2, Users } from "lucide-react"

import type { ClubWithMembers } from "@/client"
import { ClubsService } from "@/client"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface ClubHeaderProps {
  club: ClubWithMembers
}

const visibilityConfig: Record<
  string,
  { label: string; icon: typeof Globe }
> = {
  public: { label: "Public", icon: Globe },
  private: { label: "Private", icon: Lock },
  invite_only: { label: "Invite Only", icon: Lock },
}

export function ClubHeader({ club }: ClubHeaderProps) {
  const { user } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const currentMember = club.members.find((m) => m.user_id === user?.id)
  const isOwner = currentMember?.role === "owner"
  const isMember = !!currentMember && currentMember.role !== "pending"

  const visibility = visibilityConfig[club.visibility ?? "public"] ?? visibilityConfig.public
  const VisibilityIcon = visibility.icon

  const joinMutation = useMutation({
    mutationFn: () => ClubsService.joinClub({ clubId: club.id }),
    onSuccess: () => {
      showSuccessToast("Joined the club!")
      queryClient.invalidateQueries({ queryKey: ["clubs", club.id] })
    },
    onError: handleError.bind(showErrorToast),
  })

  const leaveMutation = useMutation({
    mutationFn: () => ClubsService.leaveClub({ clubId: club.id }),
    onSuccess: () => {
      showSuccessToast("Left the club")
      queryClient.invalidateQueries({ queryKey: ["clubs"] })
      navigate({ to: "/clubs" })
    },
    onError: handleError.bind(showErrorToast),
  })

  const deleteMutation = useMutation({
    mutationFn: () => ClubsService.deleteClub({ clubId: club.id }),
    onSuccess: () => {
      showSuccessToast("Club deleted")
      queryClient.invalidateQueries({ queryKey: ["clubs"] })
      navigate({ to: "/clubs" })
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <div className="space-y-4">
      {club.cover_image_url && (
        <div className="h-48 -mx-6 -mt-6 mb-6 overflow-hidden rounded-t-lg">
          <img
            src={club.cover_image_url}
            alt={club.name}
            className="w-full h-full object-cover"
          />
        </div>
      )}

      <div className="flex items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{club.name}</h1>
            <Badge variant="outline" className="gap-1">
              <VisibilityIcon className="h-3 w-3" />
              {visibility.label}
            </Badge>
          </div>

          {club.description && (
            <p className="text-muted-foreground max-w-2xl">{club.description}</p>
          )}

          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Users className="h-4 w-4" />
            <span>
              {club.member_count} {club.member_count === 1 ? "member" : "members"}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {!currentMember && (
            <Button onClick={() => joinMutation.mutate()} disabled={joinMutation.isPending}>
              Join Club
            </Button>
          )}

          {currentMember?.role === "pending" && (
            <Badge variant="secondary">Request Pending</Badge>
          )}

          {isMember && !isOwner && (
            <Button
              variant="outline"
              onClick={() => leaveMutation.mutate()}
              disabled={leaveMutation.isPending}
            >
              <LogOut className="h-4 w-4 mr-2" />
              Leave
            </Button>
          )}

          {isOwner && (
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" size="icon">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Delete Club</AlertDialogTitle>
                  <AlertDialogDescription>
                    Are you sure you want to delete this club? This action cannot
                    be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction
                    onClick={() => deleteMutation.mutate()}
                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  >
                    Delete
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          )}
        </div>
      </div>

      {club.rules && (
        <div className="p-4 bg-muted rounded-lg">
          <h3 className="font-semibold mb-2">Club Rules</h3>
          <p className="text-sm text-muted-foreground whitespace-pre-wrap">
            {club.rules}
          </p>
        </div>
      )}
    </div>
  )
}
