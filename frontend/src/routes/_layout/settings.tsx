import { createFileRoute } from "@tanstack/react-router"

import { ProfileContent } from "@/components/UserSettings/ProfileContent"
import { ProfileHeader } from "@/components/UserSettings/ProfileHeader"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
  head: () => ({
    meta: [
      {
        title: "Settings - FastAPI Cloud",
      },
    ],
  }),
})

function UserSettings() {
  const { user } = useAuth()

  if (!user) {
    return null
  }

  return (
    <div className="mx-auto w-full max-w-4xl flex flex-col gap-6 px-4 py-6 sm:px-6">
      <ProfileHeader />
      <ProfileContent />
    </div>
  )
}
