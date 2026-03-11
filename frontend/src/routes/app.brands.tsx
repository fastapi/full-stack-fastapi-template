import { createFileRoute } from "@tanstack/react-router"
import Brands from "@/components/app/Brands"

export const Route = createFileRoute("/app/brands")({
  component: Brands,
})
