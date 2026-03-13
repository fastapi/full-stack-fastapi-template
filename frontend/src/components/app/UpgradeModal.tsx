import { useNavigate } from "@tanstack/react-router"
import { Lock } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface UpgradeModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  message?: string
}

export function UpgradeModal({
  open,
  onOpenChange,
  message = "Upgrade your plan to access this feature.",
}: UpgradeModalProps) {
  const navigate = useNavigate()

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="mx-auto mb-2 rounded-full bg-slate-100 p-3">
            <Lock className="h-6 w-6 text-slate-500" />
          </div>
          <DialogTitle className="text-center">Upgrade Required</DialogTitle>
          <DialogDescription className="text-center">
            {message}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="sm:justify-center">
          <Button
            onClick={() => {
              onOpenChange(false)
              navigate({ to: "/app/pricing" })
            }}
          >
            View Plans
          </Button>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>
            Maybe Later
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
