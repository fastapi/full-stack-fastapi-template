import { useReverification, useUser } from "@clerk/clerk-react"
import { Eye, EyeOff, Loader2, Lock } from "lucide-react"
import { useState } from "react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface Props {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ChangePasswordDialog({ open, onOpenChange }: Props) {
  const { user } = useUser()
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showCurrent, setShowCurrent] = useState(false)
  const [showNew, setShowNew] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [saving, setSaving] = useState(false)
  const [errors, setErrors] = useState<{
    current?: string
    new?: string
    confirm?: string
  }>({})

  // useReverification wraps updatePassword so that if Clerk requires step-up
  // verification (email OTP), it automatically shows Clerk's verification modal
  // and retries the operation after the user completes it.
  const updatePassword = useReverification(
    (params: { currentPassword: string; newPassword: string }) =>
      user!.updatePassword({ ...params, signOutOfOtherSessions: true }),
  )

  const reset = () => {
    setCurrentPassword("")
    setNewPassword("")
    setConfirmPassword("")
    setErrors({})
    setShowCurrent(false)
    setShowNew(false)
    setShowConfirm(false)
  }

  const handleOpenChange = (value: boolean) => {
    if (!saving) {
      reset()
      onOpenChange(value)
    }
  }

  const validate = () => {
    const next: typeof errors = {}
    if (!currentPassword) next.current = "Current password is required"
    if (!newPassword) next.new = "New password is required"
    else if (newPassword.length < 8)
      next.new = "Password must be at least 8 characters"
    if (!confirmPassword) next.confirm = "Please confirm your new password"
    else if (newPassword !== confirmPassword)
      next.confirm = "Passwords do not match"
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    setSaving(true)
    try {
      await updatePassword({ currentPassword, newPassword })
      toast.success("Password updated. Other sessions have been signed out.")
      reset()
      onOpenChange(false)
    } catch (err: any) {
      const clerkMessage =
        err?.errors?.[0]?.longMessage ?? err?.errors?.[0]?.message
      if (clerkMessage?.toLowerCase().includes("current")) {
        setErrors({ current: clerkMessage })
      } else if (clerkMessage) {
        setErrors({ new: clerkMessage })
      } else {
        toast.error("Failed to update password. Please try again.")
      }
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Lock className="h-4 w-4" />
            Change Password
          </DialogTitle>
          <DialogDescription>
            Enter your current password and choose a new one.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          {/* Current password */}
          <div className="space-y-1.5">
            <Label htmlFor="cp-current">Current Password</Label>
            <div className="relative">
              <Input
                id="cp-current"
                type={showCurrent ? "text" : "password"}
                value={currentPassword}
                onChange={(e) => {
                  setCurrentPassword(e.target.value)
                  if (errors.current)
                    setErrors((p) => ({ ...p, current: undefined }))
                }}
                disabled={saving}
                className={
                  errors.current ? "border-destructive pr-10" : "pr-10"
                }
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowCurrent((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                tabIndex={-1}
              >
                {showCurrent ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
            {errors.current && (
              <p className="text-xs text-destructive">{errors.current}</p>
            )}
          </div>

          {/* New password */}
          <div className="space-y-1.5">
            <Label htmlFor="cp-new">New Password</Label>
            <div className="relative">
              <Input
                id="cp-new"
                type={showNew ? "text" : "password"}
                value={newPassword}
                onChange={(e) => {
                  setNewPassword(e.target.value)
                  if (errors.new) setErrors((p) => ({ ...p, new: undefined }))
                }}
                disabled={saving}
                className={errors.new ? "border-destructive pr-10" : "pr-10"}
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowNew((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                tabIndex={-1}
              >
                {showNew ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
            {errors.new && (
              <p className="text-xs text-destructive">{errors.new}</p>
            )}
          </div>

          {/* Confirm new password */}
          <div className="space-y-1.5">
            <Label htmlFor="cp-confirm">Confirm New Password</Label>
            <div className="relative">
              <Input
                id="cp-confirm"
                type={showConfirm ? "text" : "password"}
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value)
                  if (errors.confirm)
                    setErrors((p) => ({ ...p, confirm: undefined }))
                }}
                disabled={saving}
                className={
                  errors.confirm ? "border-destructive pr-10" : "pr-10"
                }
                autoComplete="new-password"
              />
              <button
                type="button"
                onClick={() => setShowConfirm((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                tabIndex={-1}
              >
                {showConfirm ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            </div>
            {errors.confirm && (
              <p className="text-xs text-destructive">{errors.confirm}</p>
            )}
          </div>

          <DialogFooter className="pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => handleOpenChange(false)}
              disabled={saving}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Updating...
                </>
              ) : (
                "Update Password"
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
