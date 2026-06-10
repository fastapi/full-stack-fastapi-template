import { createContext, useContext, useState } from "react"
import { cn } from "@/lib/utils"
import { Spinner } from "./ui/spinner"

type LoadingSpinnerContextType = {
  isLoading: boolean
  showSpinner: (text: string) => void
  hideSpinner: () => void
}

const LoadingSpinnerContext = createContext<LoadingSpinnerContextType | null>(
  null,
)

export function LoadingSpinnerProvider({
  children,
}: {
  children: React.ReactNode
}) {
  const [isLoading, setIsLoading] = useState(false)
  const [text, setText] = useState<string | null>(null)

  const showSpinner = (text: string) => {
    setText(text)
    setIsLoading(true)
  }

  const hideSpinner = () => setIsLoading(false)

  return (
    <LoadingSpinnerContext.Provider
      value={{ isLoading, showSpinner, hideSpinner }}
    >
      {children}
      {isLoading && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Loading"
          className={cn(
            "fixed inset-0 z-50 flex items-center justify-center",
            "bg-background/60 backdrop-blur-sm",
          )}
        >
          <Spinner className="size-10 text-primary" />
          {text && <p className="mt-4 text-lg text-foreground">{text}</p>}
        </div>
      )}
    </LoadingSpinnerContext.Provider>
  )
}

export function useLoadingSpinner() {
  const context = useContext(LoadingSpinnerContext)
  if (!context) {
    throw new Error(
      "useLoadingSpinner must be used within a LoadingSpinnerProvider",
    )
  }
  return context
}
