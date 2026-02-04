import { Star } from "lucide-react"
import { useState } from "react"

import { cn } from "@/lib/utils"

interface StarRatingProps {
  value: number
  onChange?: (value: number) => void
  readonly?: boolean
  size?: "sm" | "md" | "lg"
  className?: string
}

export function StarRating({
  value,
  onChange,
  readonly = false,
  size = "md",
  className,
}: StarRatingProps) {
  const [hoverValue, setHoverValue] = useState<number | null>(null)

  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-5 w-5",
    lg: "h-6 w-6",
  }

  const displayValue = hoverValue ?? value

  const handleClick = (rating: number) => {
    if (!readonly && onChange) {
      onChange(rating)
    }
  }

  return (
    <div
      className={cn("flex gap-0.5", className)}
      onMouseLeave={() => setHoverValue(null)}
    >
      {[1, 2, 3, 4, 5].map((star) => {
        const filled = displayValue >= star

        return (
          <button
            key={star}
            type="button"
            disabled={readonly}
            onClick={() => handleClick(star)}
            onMouseEnter={() => !readonly && setHoverValue(star)}
            className={cn(
              "transition-all",
              readonly ? "cursor-default" : "cursor-pointer hover:scale-110",
            )}
          >
            <Star
              className={cn(
                sizeClasses[size],
                filled
                  ? "fill-[var(--gold)] text-[var(--gold)]"
                  : "fill-transparent text-muted-foreground",
              )}
            />
          </button>
        )
      })}
    </div>
  )
}
