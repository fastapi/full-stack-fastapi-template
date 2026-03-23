import { useAuth } from "@clerk/clerk-react"
import { useState } from "react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"

interface Props {
  brandId: string
}

export function WeeklyReportDownloadButton({ brandId }: Props) {
  const [loading, setLoading] = useState(false)
  const { getToken } = useAuth()

  async function handleDownload() {
    setLoading(true)
    try {
      const token = await getToken()
      const res = await fetch(`/api/v1/reports/weekly/${brandId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.status === 404) {
        toast.error("Report not available — check back after Monday.")
        return
      }
      if (!res.ok) throw new Error("Download failed")
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      const disposition = res.headers.get("Content-Disposition") ?? ""
      const match = disposition.match(/filename="(.+)"/)
      a.download = match?.[1] ?? `kila-report-${brandId}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      toast.error("Failed to download report.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Button variant="outline" onClick={handleDownload} disabled={loading}>
      {loading ? "Downloading..." : "Download Weekly Report"}
    </Button>
  )
}
