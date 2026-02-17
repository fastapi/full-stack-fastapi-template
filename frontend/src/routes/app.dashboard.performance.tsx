import { createFileRoute } from "@tanstack/react-router"
import { BrandPerformanceDetail } from "@/components/app/dashboard/BrandPerformanceDetail"

export const Route = createFileRoute("/app/dashboard/performance")({
  component: BrandPerformanceDetail,
})
