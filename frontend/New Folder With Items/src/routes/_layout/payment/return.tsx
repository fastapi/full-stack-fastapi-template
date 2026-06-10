import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link, useSearch } from "@tanstack/react-router"
import { CheckCircle2, Loader2, XCircle } from "lucide-react"
import { z } from "zod"

import { OpenAPI } from "@/client/core/OpenAPI"
import { request } from "@/client/core/request"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

// VNPAY appends these query params to the return URL
// Use z.coerce.string() because VNPAY sends some params as numbers (e.g. vnp_Amount, vnp_TxnRef, vnp_PayDate)
const vnpaySearchSchema = z.object({
  vnp_ResponseCode: z.coerce.string().optional(),
  vnp_TxnRef: z.coerce.string().optional(),
  vnp_Amount: z.coerce.string().optional(),
  vnp_OrderInfo: z.coerce.string().optional(),
  vnp_BankCode: z.coerce.string().optional(),
  vnp_BankTranNo: z.coerce.string().optional(),
  vnp_CardType: z.coerce.string().optional(),
  vnp_PayDate: z.coerce.string().optional(),
  vnp_TransactionNo: z.coerce.string().optional(),
  vnp_TransactionStatus: z.coerce.string().optional(),
  vnp_TmnCode: z.coerce.string().optional(),
  vnp_SecureHash: z.coerce.string().optional(),
})

export const Route = createFileRoute("/_layout/payment/return")({
  validateSearch: vnpaySearchSchema,
  component: PaymentReturnPage,
  head: () => ({
    meta: [{ title: "Payment Result - FastAPI Template" }],
  }),
})

function formatVND(raw: string | undefined): string {
  if (!raw) return "—"
  const amount = parseInt(raw, 10) / 100
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(amount)
}

function formatPayDate(raw: string | undefined): string {
  if (!raw || raw.length !== 14) return "—"
  // Format: YYYYMMDDHHmmss
  const y = raw.slice(0, 4)
  const mo = raw.slice(4, 6)
  const d = raw.slice(6, 8)
  const h = raw.slice(8, 10)
  const mi = raw.slice(10, 12)
  const s = raw.slice(12, 14)
  return `${d}/${mo}/${y} ${h}:${mi}:${s}`
}

function PaymentReturnPage() {
  const search = useSearch({ from: "/_layout/payment/return" })

  // Call the backend to process the payment and update the balance
  const { isLoading, isError } = useQuery({
    queryKey: ["payment-return", search.vnp_TxnRef],
    queryFn: () => {
      const params = new URLSearchParams()
      Object.entries(search).forEach(([k, v]) => {
        if (v !== undefined) params.set(k, v)
      })
      return request(OpenAPI, {
        method: "GET",
        url: "/api/v1/topup/return",
        query: Object.fromEntries(params),
      })
    },
    retry: false,
    staleTime: Infinity, // only process once
  })

  const isSuccess =
    search.vnp_ResponseCode === "00" && search.vnp_TransactionStatus === "00"

  if (isLoading) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center">
        <Loader2 className="h-10 w-10 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4">
      <Card className="w-full max-w-lg shadow-lg">
        <CardHeader className="flex flex-col items-center gap-2 pb-2">
          {isSuccess ? (
            <CheckCircle2 className="h-16 w-16 text-green-500" />
          ) : (
            <XCircle className="h-16 w-16 text-red-500" />
          )}
          <CardTitle className="text-center text-2xl">
            {isSuccess ? "Payment Successful" : "Payment Failed"}
          </CardTitle>
          <p className="text-center text-sm text-muted-foreground">
            {isSuccess
              ? "Your balance has been topped up successfully."
              : isError
                ? "Payment processed but failed to update balance. Please contact support."
                : "Your payment could not be processed. Please try again."}
          </p>
        </CardHeader>

        <CardContent>
          <dl className="divide-y rounded-lg border text-sm">
            <Row label="Transaction Ref" value={search.vnp_TxnRef ?? "—"} />
            <Row label="Amount" value={formatVND(search.vnp_Amount)} />
            <Row label="Bank" value={search.vnp_BankCode ?? "—"} />
            <Row label="Card Type" value={search.vnp_CardType ?? "—"} />
            <Row label="Bank Tran No." value={search.vnp_BankTranNo ?? "—"} />
            <Row
              label="Transaction No."
              value={search.vnp_TransactionNo ?? "—"}
            />
            <Row label="Date" value={formatPayDate(search.vnp_PayDate)} />
            <Row label="Description" value={search.vnp_OrderInfo ?? "—"} />
            <Row
              label="Status"
              value={isSuccess ? "Success" : "Failed"}
              valueClassName={
                isSuccess
                  ? "text-green-600 font-medium"
                  : "text-red-600 font-medium"
              }
            />
          </dl>
        </CardContent>

        <CardFooter className="flex gap-3">
          <Button asChild className="flex-1">
            <Link to="/topup">Top Up Again</Link>
          </Button>
          <Button asChild variant="outline" className="flex-1">
            <Link to="/dashboard">Go to Dashboard</Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}

function Row({
  label,
  value,
  valueClassName,
}: {
  label: string
  value: string
  valueClassName?: string
}) {
  return (
    <div className="flex justify-between px-4 py-2">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className={valueClassName}>{value}</dd>
    </div>
  )
}
