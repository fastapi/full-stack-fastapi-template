import { useAuth } from "@clerk/clerk-react"
import { createFileRoute, Outlet, useNavigate } from "@tanstack/react-router"
import { useEffect, useState } from "react"
import AppLayout from "@/components/app/AppLayout"
import { SubscriptionContext } from "@/contexts/SubscriptionContext"
import type { UserSubscription } from "@/lib/entitlements"

export const Route = createFileRoute("/app")({
  component: AppGuard,
})

function AppGuard() {
  const { isLoaded, isSignedIn, getToken } = useAuth()
  const navigate = useNavigate()
  const [syncState, setSyncState] = useState<"loading" | "synced" | "error">(
    "loading",
  )
  const [profileComplete, setProfileComplete] = useState(false)
  const [_retryCount, setRetryCount] = useState(0)
  const [subscription, setSubscription] = useState<UserSubscription | null>(
    null,
  )

  useEffect(() => {
    if (!isLoaded) return

    if (!isSignedIn) {
      navigate({ to: "/" })
      return
    }

    // Sync with backend to check profile status
    const syncUser = async () => {
      try {
        const token = await getToken()
        if (!token) {
          console.error("No Clerk token available")
          setSyncState("error")
          return
        }

        const apiUrl = import.meta.env.VITE_API_URL ?? ""
        const response = await fetch(`${apiUrl}/api/v1/auth/clerk-sync`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        })

        if (response.ok) {
          const data = await response.json()
          setProfileComplete(data.profile_complete)
          setSyncState("synced")

          // Load subscription from profile endpoint
          const profileResponse = await fetch(`${apiUrl}/api/v1/profile/me`, {
            headers: { Authorization: `Bearer ${token}` },
          })
          if (profileResponse.ok) {
            const profileData = await profileResponse.json()
            if (profileData?.subscription) {
              setSubscription(profileData.subscription)
            }
          }
        } else {
          console.error("clerk-sync failed:", response.status)
          setSyncState("error")
        }
      } catch (error) {
        console.error("Failed to sync user:", error)
        setSyncState("error")
      }
    }

    syncUser()
  }, [isLoaded, isSignedIn, getToken, navigate])

  // Redirect to profile setup if not complete (moved to useEffect to avoid setState-in-render)
  useEffect(() => {
    if (
      syncState === "synced" &&
      !profileComplete &&
      !window.location.pathname.includes("/profile-setup")
    ) {
      navigate({ to: "/app/profile-setup" })
    }
  }, [syncState, profileComplete, navigate])

  // Still loading Clerk or syncing with backend
  if (!isLoaded || syncState === "loading") {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  if (!isSignedIn) {
    return null
  }

  // Backend sync failed — show error with retry
  if (syncState === "error") {
    return (
      <div className="h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 gap-4">
        <p className="text-gray-600 dark:text-gray-400">
          Failed to connect to server. Please try again.
        </p>
        <button
          type="button"
          onClick={() => {
            setSyncState("loading")
            setRetryCount((c) => c + 1)
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <SubscriptionContext.Provider value={{ subscription }}>
      <AppLayout>
        <Outlet />
      </AppLayout>
    </SubscriptionContext.Provider>
  )
}
