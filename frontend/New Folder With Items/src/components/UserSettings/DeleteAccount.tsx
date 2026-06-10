import { AlertCircle, Trash2 } from "lucide-react"

import { Alert, AlertDescription } from "@/components/ui/alert"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import DeleteConfirmation from "./DeleteConfirmation"

const DeleteAccount = () => {
  return (
    <Card className="border-destructive/50">
      <CardHeader className="flex flex-row items-start gap-2 pb-4">
        <Trash2 className="h-5 w-5 mt-0.5 shrink-0 text-destructive" />
        <div>
          <CardTitle className="text-lg text-destructive">
            Delete Account
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            Permanently delete your account and all associated data
          </p>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <Alert
          variant="destructive"
          className="bg-destructive/5 border-destructive/30"
        >
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-destructive text-sm">
            <strong>This action cannot be undone</strong>
            <br />
            All your data, including templates and usage history, will be
            permanently deleted.
          </AlertDescription>
        </Alert>
        <DeleteConfirmation />
      </CardContent>
    </Card>
  )
}

export default DeleteAccount
