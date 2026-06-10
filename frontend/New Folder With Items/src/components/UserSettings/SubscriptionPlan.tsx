import { Link } from "@tanstack/react-router"
import { XCircle, Zap } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const SubscriptionPlan = () => {
  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between pb-4">
        <div className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-primary" />
          <div>
            <CardTitle className="text-lg">Subscription Plan</CardTitle>
            <p className="text-sm text-muted-foreground">
              Manage your subscription and billing
            </p>
          </div>
        </div>
        <Badge variant="secondary" className="shrink-0">
          Free Demo
        </Badge>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <XCircle className="h-4 w-4 shrink-0" />
          <span>No active subscription</span>
        </div>
        <p className="text-sm text-muted-foreground">
          Upgrade to unlock more pages, files, and advanced features.
        </p>
        <Link to="/pricing">
          <Button className="gap-2">
            <Zap className="h-4 w-4" />
            Upgrade Now
          </Button>
        </Link>
      </CardContent>
    </Card>
  )
}

export default SubscriptionPlan
