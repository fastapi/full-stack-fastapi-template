import { createFileRoute } from "@tanstack/react-router"
import UserProfile from "@/components/app/UserProfile"

export const Route = createFileRoute("/app/users")({
  component: UserProfile,
})
