import { createFileRoute } from "@tanstack/react-router"
import Projects from "@/components/app/Projects"

export const Route = createFileRoute("/app/projects")({
  component: Projects,
})
