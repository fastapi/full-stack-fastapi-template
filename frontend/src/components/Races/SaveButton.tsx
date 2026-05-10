import { useState } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Bookmark, BookmarkCheck } from "lucide-react"
import { ProfilesService } from "@/client"
import { cn } from "@/lib/utils"

interface SaveButtonProps {
  raceId: string
  isSaved: boolean
  className?: string
}

export function SaveButton({ raceId, isSaved: initialSaved, className }: SaveButtonProps) {
  const queryClient = useQueryClient()
  // Optimistic local state
  const [saved, setSaved] = useState(initialSaved)

  const save = useMutation({
    mutationFn: () => ProfilesService.saveRace({ raceId }),
    onMutate: () => setSaved(true),
    onError: () => setSaved(initialSaved),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["savedRaces"] }),
  })

  const unsave = useMutation({
    mutationFn: () => ProfilesService.unsaveRace({ raceId }),
    onMutate: () => setSaved(false),
    onError: () => setSaved(initialSaved),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["savedRaces"] }),
  })

  const isPending = save.isPending || unsave.isPending

  return (
    <button
      type="button"
      disabled={isPending}
      onClick={() => (saved ? unsave.mutate() : save.mutate())}
      title={saved ? "Remove from saved" : "Save race"}
      className={cn(
        "inline-flex items-center justify-center rounded-md p-2 transition-colors",
        "hover:bg-muted disabled:opacity-50",
        saved ? "text-primary" : "text-muted-foreground",
        className
      )}
    >
      {saved ? <BookmarkCheck className="size-5" /> : <Bookmark className="size-5" />}
    </button>
  )
}
