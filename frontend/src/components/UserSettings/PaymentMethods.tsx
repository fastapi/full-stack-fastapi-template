import { Link } from "@tanstack/react-router"
import { CreditCard } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const PaymentMethods = () => {
  return (
    <Card>
      <CardHeader className="flex flex-row items-start gap-2 pb-4">
        <CreditCard className="h-5 w-5 mt-0.5 shrink-0" />
        <div>
          <CardTitle className="text-lg">Payment Methods</CardTitle>
          <p className="text-sm text-muted-foreground">
            Manage your payment information
          </p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center justify-center py-8 gap-4 text-center">
          <CreditCard className="h-12 w-12 text-muted-foreground/40" />
          <p className="text-sm text-muted-foreground">
            No payment methods on file
          </p>
          <Link to="/pricing">
            <Button variant="outline" size="sm">
              Subscribe to Add Payment
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  )
}

export default PaymentMethods
