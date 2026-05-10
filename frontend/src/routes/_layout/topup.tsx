import { useMutation, useQuery, useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import {
  ArrowDownCircle,
  ArrowUpCircle,
  CheckCircle,
  Clock,
  RefreshCw,
  Wallet,
  XCircle,
} from "lucide-react"
import { Suspense, useState } from "react"

import { type TopupPackage, TopupService } from "@/client"
import type { TopupTransactionPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/topup")({
  component: PaymentPage,
  head: () => ({
    meta: [{ title: "Payment - FastAPI Template" }],
  }),
})

// ─── Formatters ─────────────────────────────────────────────────────────────

function formatVND(amount: number): string {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(amount)
}

function formatDate(dateStr: string): string {
  return new Intl.DateTimeFormat("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(dateStr))
}

// ─── Balance Card ────────────────────────────────────────────────────────────

function BalanceCard() {
  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["myBalance"],
    queryFn: () => TopupService.getMyBalance(),
  })

  return (
    <Card className="bg-linear-to-br from-primary/10 to-primary/5 border-primary/20">
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground font-medium">
              Available Balance
            </p>
            {isLoading ? (
              <Skeleton className="h-9 w-40" />
            ) : (
              <p className="text-3xl font-bold tracking-tight">
                {formatVND(data?.balance ?? 0)}
              </p>
            )}
            {data?.updated_at && (
              <p className="text-xs text-muted-foreground">
                Updated {formatDate(data.updated_at)}
              </p>
            )}
          </div>
          <div className="flex flex-col items-center gap-2">
            <div className="rounded-full bg-primary/10 p-4">
              <Wallet className="h-7 w-7 text-primary" />
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 px-2 text-xs text-muted-foreground"
              onClick={() => refetch()}
              disabled={isFetching}
            >
              <RefreshCw
                className={`h-3 w-3 mr-1 ${isFetching ? "animate-spin" : ""}`}
              />
              Refresh
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// ─── Package Grid ─────────────────────────────────────────────────────────────

function PackageGrid({
  selected,
  onSelect,
}: {
  selected: TopupPackage | null
  onSelect: (pkg: TopupPackage) => void
}) {
  const { data } = useSuspenseQuery({
    queryKey: ["topupPackages"],
    queryFn: () => TopupService.getTopupPackages(),
  })

  const packages = data.packages ?? []

  return (
    <div className="grid grid-cols-3 gap-3">
      {packages.map((pkg) => {
        const isSelected = selected?.id === pkg.id
        return (
          <button
            key={pkg.id}
            type="button"
            onClick={() => onSelect(pkg)}
            className={`relative rounded-xl border-2 p-4 text-center transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
              isSelected
                ? "border-primary bg-primary/10 shadow-md"
                : "border-border hover:border-primary/50 hover:bg-muted/50"
            }`}
          >
            {isSelected && (
              <CheckCircle className="absolute top-2 right-2 h-4 w-4 text-primary" />
            )}
            <p className="text-base font-semibold">{formatVND(pkg.amount)}</p>
          </button>
        )
      })}
    </div>
  )
}

function PackageGridSkeleton() {
  return (
    <div className="grid grid-cols-3 gap-3">
      {Array.from({ length: 9 }).map((_, i) => (
        // biome-ignore lint/suspicious/noArrayIndexKey: static skeleton list
        <Skeleton key={i} className="h-16 rounded-xl" />
      ))}
    </div>
  )
}

// ─── QR Code Display ─────────────────────────────────────────────────────────

function QRCodeDisplay({ url }: { url: string }) {
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(url)}`
  return (
    <div className="flex flex-col items-center gap-4 mt-4">
      <img
        src={qrUrl}
        alt="VNPAY QR Code"
        className="rounded-xl border shadow-sm"
        width={220}
        height={220}
      />
      <p className="text-sm text-muted-foreground text-center max-w-xs">
        Scan this QR code with your VNPAY-supported banking app to complete the
        payment.
      </p>
      <Button variant="outline" size="sm" asChild>
        <a href={url} target="_blank" rel="noopener noreferrer">
          Open payment page
        </a>
      </Button>
    </div>
  )
}

// ─── Top-up Section ───────────────────────────────────────────────────────────

function TopupSection({ onSuccess }: { onSuccess: () => void }) {
  const [selected, setSelected] = useState<TopupPackage | null>(null)
  const [paymentUrl, setPaymentUrl] = useState<string | null>(null)
  const { showSuccessToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: (amount: number) =>
      TopupService.createPayment({ requestBody: { amount } }),
    onSuccess: (data) => {
      setPaymentUrl(data.payment_url)
      showSuccessToast("QR code generated! Scan to pay.")
      onSuccess()
    },
    onError: handleError,
  })

  const handleGenerate = () => {
    if (!selected) return
    setPaymentUrl(null)
    mutation.mutate(selected.amount)
  }

  const handleSelectPackage = (pkg: TopupPackage) => {
    setSelected(pkg)
    setPaymentUrl(null)
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <ArrowUpCircle className="h-5 w-5 text-primary" />
            Select a top-up amount
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Suspense fallback={<PackageGridSkeleton />}>
            <PackageGrid selected={selected} onSelect={handleSelectPackage} />
          </Suspense>

          {selected && (
            <div className="flex items-center justify-between rounded-lg bg-muted/50 px-4 py-2">
              <span className="text-sm text-muted-foreground">Selected</span>
              <Badge variant="secondary" className="text-sm font-semibold">
                {formatVND(selected.amount)}
              </Badge>
            </div>
          )}

          <Button
            className="w-full"
            disabled={!selected || mutation.isPending}
            onClick={handleGenerate}
          >
            {mutation.isPending ? "Generating…" : "Generate QR Code"}
          </Button>
        </CardContent>
      </Card>

      {paymentUrl && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Scan to pay</CardTitle>
          </CardHeader>
          <CardContent>
            <QRCodeDisplay url={paymentUrl} />
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// ─── Transaction Status Badge ─────────────────────────────────────────────────

function StatusBadge({ status }: { status: TopupTransactionPublic["status"] }) {
  if (status === "success") {
    return (
      <Badge
        variant="secondary"
        className="bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 gap-1"
      >
        <CheckCircle className="h-3 w-3" />
        Success
      </Badge>
    )
  }
  if (status === "failed") {
    return (
      <Badge
        variant="secondary"
        className="bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 gap-1"
      >
        <XCircle className="h-3 w-3" />
        Failed
      </Badge>
    )
  }
  return (
    <Badge
      variant="secondary"
      className="bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400 gap-1"
    >
      <Clock className="h-3 w-3" />
      Pending
    </Badge>
  )
}

// ─── Transaction History ──────────────────────────────────────────────────────

function TransactionHistory({ refreshKey }: { refreshKey: number }) {
  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["myTransactions", refreshKey],
    queryFn: () => TopupService.getMyTransactions({ limit: 50 }),
  })

  const transactions = data ?? []

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <ArrowDownCircle className="h-5 w-5 text-primary" />
            Transaction History
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
            className="h-8 px-2"
          >
            <RefreshCw
              className={`h-4 w-4 ${isFetching ? "animate-spin" : ""}`}
            />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        {isLoading ? (
          <div className="p-6 space-y-3">
            {Array.from({ length: 5 }).map((_, i) => (
              // biome-ignore lint/suspicious/noArrayIndexKey: static skeleton list
              <Skeleton key={i} className="h-12 w-full rounded-md" />
            ))}
          </div>
        ) : transactions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
            <Wallet className="h-10 w-10 mb-3 opacity-30" />
            <p className="text-sm font-medium">No transactions yet</p>
            <p className="text-xs mt-1">
              Your payment history will appear here.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Reference</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                  <TableHead className="text-center">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {transactions.map((txn) => (
                  <TableRow key={txn.id}>
                    <TableCell className="text-sm text-muted-foreground whitespace-nowrap">
                      {formatDate(txn.created_at)}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-muted-foreground max-w-30 truncate">
                      {txn.txn_ref ?? "—"}
                    </TableCell>
                    <TableCell>
                      {txn.type === "credit" ? (
                        <span className="inline-flex items-center gap-1 text-sm text-green-600 dark:text-green-400 font-medium">
                          <ArrowUpCircle className="h-3.5 w-3.5" />
                          Credit
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-sm text-orange-600 dark:text-orange-400 font-medium">
                          <ArrowDownCircle className="h-3.5 w-3.5" />
                          Debit
                        </span>
                      )}
                    </TableCell>
                    <TableCell
                      className={`text-right font-semibold ${
                        txn.type === "credit"
                          ? "text-green-600 dark:text-green-400"
                          : "text-orange-600 dark:text-orange-400"
                      }`}
                    >
                      {txn.type === "credit" ? "+" : "-"}
                      {formatVND(txn.amount)}
                    </TableCell>
                    <TableCell className="text-center">
                      <StatusBadge status={txn.status} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────────

function PaymentPage() {
  const [historyKey, setHistoryKey] = useState(0)

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Payment</h1>
        <p className="text-muted-foreground">
          Manage your balance and view payment history
        </p>
      </div>

      <BalanceCard />

      <Separator />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        <TopupSection onSuccess={() => setHistoryKey((k) => k + 1)} />
        <TransactionHistory refreshKey={historyKey} />
      </div>
    </div>
  )
}
