import { ThumbsDown, ThumbsUp } from "lucide-react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface VoteButtonsProps {
  upvotes: number
  downvotes: number
  userVote: "upvote" | "downvote" | null
  onVote: (voteType: "upvote" | "downvote") => void
  disabled?: boolean
}

export function VoteButtons({
  upvotes,
  downvotes,
  userVote,
  onVote,
  disabled = false,
}: VoteButtonsProps) {
  return (
    <div className="flex items-center gap-2">
      <Button
        variant="ghost"
        size="sm"
        className={cn(
          "gap-1",
          userVote === "upvote" && "text-green-500 bg-green-500/10"
        )}
        onClick={() => onVote("upvote")}
        disabled={disabled}
      >
        <ThumbsUp className="h-4 w-4" />
        <span>{upvotes}</span>
      </Button>
      <Button
        variant="ghost"
        size="sm"
        className={cn(
          "gap-1",
          userVote === "downvote" && "text-red-500 bg-red-500/10"
        )}
        onClick={() => onVote("downvote")}
        disabled={disabled}
      >
        <ThumbsDown className="h-4 w-4" />
        <span>{downvotes}</span>
      </Button>
    </div>
  )
}
