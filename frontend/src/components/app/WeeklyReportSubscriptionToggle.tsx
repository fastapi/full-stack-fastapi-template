import { useAuth } from "@clerk/clerk-react"
import { useEffect, useState } from "react"
import { toast } from "sonner"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"

interface Props {
  brandId: string
}

export function WeeklyReportSubscriptionToggle({ brandId }: Props) {
  const [isActive, setIsActive] = useState(false)
  const [loading, setLoading] = useState(true)
  const { getToken } = useAuth()

  useEffect(() => {
    let cancelled = false
    async function fetchStatus() {
      try {
        const token = await getToken()
        const r = await fetch(
          `/api/v1/brands/${brandId}/reports/weekly/subscription`,
          { headers: { Authorization: `Bearer ${token}` } },
        )
        const data = await r.json()
        if (!cancelled) setIsActive(data.is_active ?? false)
      } catch {
        // ignore fetch errors on load
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    fetchStatus()
    return () => {
      cancelled = true
    }
  }, [brandId, getToken])

  async function handleToggle(checked: boolean) {
    setIsActive(checked)
    try {
      const token = await getToken()
      await fetch(`/api/v1/brands/${brandId}/reports/weekly/subscription`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ is_active: checked }),
      })
    } catch {
      // Revert on error
      setIsActive(!checked)
      toast.error("Failed to update subscription preference.")
    }
  }

  return (
    <div className="flex items-start gap-3">
      <Checkbox
        id="weekly-report-toggle"
        checked={isActive}
        onCheckedChange={(checked) => handleToggle(checked === true)}
        disabled={loading}
        className="mt-0.5"
      />
      <div>
        <Label
          htmlFor="weekly-report-toggle"
          className="font-medium cursor-pointer"
        >
          Email me the weekly report every Monday
        </Label>
        <p className="text-sm text-slate-500">
          Delivered every Monday at 8:00 AM UTC
        </p>
      </div>
    </div>
  )
}
