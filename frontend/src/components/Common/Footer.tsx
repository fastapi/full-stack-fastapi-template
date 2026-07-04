import { useQuery } from "@tanstack/react-query"

async function fetchStats(): Promise<{
  total: number
  lastUpdated: string | null
}> {
  const res = await fetch(
    `${import.meta.env.VITE_API_URL}/api/v1/articles/stats`,
  )
  if (!res.ok) return { total: 0, lastUpdated: null }
  return res.json()
}

function formatLastUpdated(iso: string | null): string {
  if (!iso) return ""
  try {
    const d = new Date(`${iso}Z`)
    const diffMs = Date.now() - d.getTime()
    const diffH = Math.floor(diffMs / 3_600_000)
    if (diffH < 1) return "Updated just now"
    if (diffH < 24) return `Updated ${diffH}h ago`
    const diffD = Math.floor(diffH / 24)
    return `Updated ${diffD}d ago`
  } catch {
    return ""
  }
}

export function Footer() {
  const { data } = useQuery({
    queryKey: ["stats"],
    queryFn: fetchStats,
    staleTime: 5 * 60_000,
  })

  const total = data?.total ?? 0
  const updatedLabel = formatLastUpdated(data?.lastUpdated ?? null)

  return (
    <footer className="border-t">
      <div className="mx-auto flex max-w-3xl flex-wrap items-center justify-between gap-3 px-4 py-4">
        <div className="flex items-center gap-4">
          {total > 0 && (
            <span className="font-mono text-[11px] text-muted-foreground">
              {total.toLocaleString()} articles curated
            </span>
          )}
          {updatedLabel && (
            <>
              <span className="text-border">·</span>
              <span className="font-mono text-[11px] text-muted-foreground">
                {updatedLabel}
              </span>
            </>
          )}
        </div>
      </div>
    </footer>
  )
}
