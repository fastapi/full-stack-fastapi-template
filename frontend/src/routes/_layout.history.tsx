import { createFileRoute, useParams } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { RaceRegistrationsService } from "@/client"
import type { RaceRegistrationPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Calendar, Clock } from "lucide-react"
import { Link } from "@tanstack/react-router"
import { cn } from "@/lib/utils"

export const Route = createFileRoute("/_layout/history")({
  component: RaceHistoryPage,
  head: () => ({
    meta: [{ title: "My Race History - VNRunner" }],
  }),
})

const STATUS_COLORS: Record<string, string> = {
  confirmed: "bg-green-100 text-green-800",
  pending: "bg-yellow-100 text-yellow-800",
  cancelled: "bg-red-100 text-red-800",
  waitlist: "bg-blue-100 text-blue-800",
}

const PAYMENT_COLORS: Record<string, string> = {
  paid: "bg-green-100 text-green-800",
  unpaid: "bg-yellow-100 text-yellow-800",
  refunded: "bg-gray-100 text-gray-800",
  partial: "bg-orange-100 text-orange-800",
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  })
}

function RegistrationRow({ reg }: { reg: RaceRegistrationPublic }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-lg border p-4 hover:bg-muted/30 transition-colors">
      <div className="space-y-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-medium truncate">Registration #{reg.id.slice(0, 8)}</span>
          {reg.bib_number && (
            <Badge variant="outline">Bib #{reg.bib_number}</Badge>
          )}
        </div>
        <div className="flex items-center gap-4 text-sm text-muted-foreground flex-wrap">
          <span className="flex items-center gap-1">
            <Calendar className="size-3.5" />
            {formatDate(reg.registered_at)}
          </span>
          {reg.amount_paid != null && (
            <span>{reg.amount_paid.toLocaleString()} VND</span>
          )}
        </div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        {reg.registration_status && (
          <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-medium", STATUS_COLORS[reg.registration_status] ?? "bg-gray-100 text-gray-700")}>
            {reg.registration_status}
          </span>
        )}
        {reg.payment_status && (
          <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-medium", PAYMENT_COLORS[reg.payment_status] ?? "bg-gray-100 text-gray-700")}>
            {reg.payment_status}
          </span>
        )}
      </div>
    </div>
  )
}

function RaceHistoryPage() {
  const [tab, setTab] = useState<"upcoming" | "past">("upcoming")
  const params = useParams({ strict: false }) as Record<string, any>
  const { i18n } = useTranslation()
  const lang = params?.lang || i18n.language || "vi"

  const { data, isLoading } = useQuery({
    queryKey: ["myRegistrations"],
    queryFn: () => RaceRegistrationsService.readMyRegistrations({ limit: 100 }),
  })

  const regs = data?.data ?? []
  // const now = new Date() // Future use for filtering by date

  const upcoming = regs.filter(
    (r) => r.registration_status !== "cancelled"
  )
  const past = regs.filter(
    (r) => r.registration_status === "cancelled"
  )

  const displayed = tab === "upcoming" ? upcoming : past

  const stats = {
    total: regs.length,
    confirmed: regs.filter((r) => r.registration_status === "confirmed").length,
    paid: regs.filter((r) => r.payment_status === "paid").length,
  }

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight">Race History</h1>
        <p className="text-muted-foreground">All your race registrations.</p>
      </div>

      {/* Stats summary */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Total Registrations", value: stats.total },
          { label: "Confirmed", value: stats.confirmed },
          { label: "Paid", value: stats.paid },
        ].map(({ label, value }) => (
          <div key={label} className="rounded-lg border p-4 text-center">
            <div className="text-2xl font-bold">{value}</div>
            <div className="text-xs text-muted-foreground mt-1">{label}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-md border p-1 w-fit">
        {(["upcoming", "past"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              "rounded px-4 py-1.5 text-sm font-medium capitalize transition-colors",
              tab === t ? "bg-muted text-foreground" : "text-muted-foreground hover:text-foreground"
            )}
          >
            {t}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-20 rounded-lg" />
          ))}
        </div>
      ) : displayed.length === 0 ? (
        <div className="py-12 text-center space-y-2">
          <Clock className="mx-auto size-10 text-muted-foreground/50" />
          <p className="text-muted-foreground">No {tab} registrations.</p>
          {tab === "upcoming" && (
            <Link to="/$lang/races" params={{ lang }} className="text-sm text-primary hover:underline">
              Browse upcoming races →
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {displayed.map((reg) => (
            <RegistrationRow key={reg.id} reg={reg} />
          ))}
        </div>
      )}
    </div>
  )
}
