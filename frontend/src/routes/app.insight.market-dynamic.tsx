import { createFileRoute } from "@tanstack/react-router"
import MarketDynamic from "@/components/app/insight/MarketDynamic"

export const Route = createFileRoute("/app/insight/market-dynamic")({
  component: MarketDynamic,
})
