import { Key } from "lucide-react"
import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import useAuth from "@/hooks/useAuth"
import ChangePassword from "./ChangePassword"

export function AccountSecurityCard() {
  const { user } = useAuth()
  const [changePasswordOpen, setChangePasswordOpen] = useState(false)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Account</CardTitle>
        <CardDescription>
          Manage your account status and password.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1">
            <Label className="text-base font-medium">Account status</Label>
            <p className="text-muted-foreground text-sm">
              Your account is currently active.
            </p>
          </div>
          <Badge
            variant="outline"
            className={
              user?.is_active
                ? "shrink-0 border-green-200 bg-green-50 text-green-700 dark:border-green-900 dark:bg-green-950 dark:text-green-400"
                : "shrink-0 border-muted text-muted-foreground"
            }
          >
            {user?.is_active ? "Active" : "Inactive"}
          </Badge>
        </div>

        <Separator />

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1">
            <Label className="text-base font-medium">Password</Label>
            <p className="text-muted-foreground text-sm">
              Update your password.
            </p>
          </div>
          <Dialog
            open={changePasswordOpen}
            onOpenChange={setChangePasswordOpen}
          >
            <DialogTrigger asChild>
              <Button type="button" variant="outline" className="shrink-0">
                <Key className="mr-2 h-4 w-4" aria-hidden />
                Change password
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Change password</DialogTitle>
                <DialogDescription>
                  Enter your current password and choose a new one.
                </DialogDescription>
              </DialogHeader>
              <ChangePassword
                onSuccess={() => setChangePasswordOpen(false)}
                embedded
              />
            </DialogContent>
          </Dialog>
        </div>
      </CardContent>
    </Card>
  )
}
